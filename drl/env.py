import traci
import numpy as np


class TransitEnv:

    def __init__(self, sumo_cfg):
        self.sumo_cfg = sumo_cfg
        self.step_length = 60
        self.target_headway = 600  # 10 minutes
        self.last_dispatch_time = 0

        # ===== Configuration =====
        #self.route_id = "AB097"
        self.max_stops = 15      # 15 stops × 4 features = 60
        self.max_vehicles = 6    # 6 vehicles × 6 features = 36

        self.route_ids = ["0", "1"]
        self.direction_toggle = 0
        self.pending_delay = 0

    # ==========================
    # Simulation Control
    # ==========================
    def start(self):
        # This forces the simulation to stay open from 21590 to 30000 seconds
        traci.start([
            "sumo", "-c", self.sumo_cfg,
            "--begin", "21590",
            "--end", "30000",
            "--waiting-time-memory", "1000" 
        ])

    def close(self):
        """Cleanly shut down TraCI."""
        try:
            import traci
            traci.close()
        except Exception as e:
            print(f"Error during TraCI closure: {e}")
    
    
    def reset(self):
        try:
            traci.close()
        except:
            pass
        self.start()
        
        # Fast-forward to the time when buses actually start (21590)
        start_time = 21590
        traci.simulationStep(start_time) 
        
        self.last_dispatch_time = start_time
        self.direction_toggle = 0
        self.pending_delay = 0
        return self.get_state()

    def step(self, action):
        self.apply_action(action)

        for _ in range(self.step_length):
            traci.simulationStep()

        next_state = self.get_state()
        reward = self.compute_reward()
        
        # End episode after time 28000 (roughly 2 hours of sim time)
        current_time = traci.simulation.getTime()
        done = current_time >= 28000 

        return next_state, reward, done

    # ==========================
    # STATE (112 Dimensions)
    # ==========================
    def get_state(self):

        stop_features = self.get_stop_features()        # 60
        vehicle_features = self.get_vehicle_features()  # 36
        network_features = self.get_network_features()  # 16

        state = np.concatenate([
            stop_features,
            vehicle_features,
            network_features
        ])

        return state.astype(np.float32)

    # --------------------------
    # 1️⃣ STOP-LEVEL (60)
    # 15 stops × 4 features:
    # [waiting_count, avg_wait, last_arrival_gap, queue_growth]
    # --------------------------
    def get_stop_features(self):

        stops = traci.busstop.getIDList()
        features = []

        for stop in stops[:self.max_stops]:

            waiting = traci.busstop.getPersonCount(stop)

            # average waiting time
            persons = traci.busstop.getPersonIDs(stop)
            if len(persons) > 0:
                waits = [traci.person.getWaitingTime(p) for p in persons]
                avg_wait = np.mean(waits)
            else:
                avg_wait = 0

            # time since last vehicle at stop
            last_arrival = traci.busstop.getVehicleIDs(stop)
            gap = len(last_arrival)

            # queue growth approximation
            queue_growth = waiting / (avg_wait + 1)

            features.extend([
                waiting,
                avg_wait,
                gap,
                queue_growth
            ])

        # padding if fewer than max_stops
        while len(features) < self.max_stops * 4:
            features.append(0)

        return np.array(features[:60])

    # --------------------------
    # 2️⃣ VEHICLE-LEVEL (36)
    # 6 vehicles × 6 features:
    # [load, speed, distance_to_next_stop,
    #  schedule_deviation, dwell_time, headway_dev]
    # --------------------------
    def get_vehicle_features(self):

        vehicles = traci.vehicle.getIDList()
        features = []

        for veh in vehicles[:self.max_vehicles]:

            load = traci.vehicle.getPersonNumber(veh)
            speed = traci.vehicle.getSpeed(veh)

            # approximate distance to next stop
            try:
                next_stop = traci.vehicle.getNextStops(veh)[0][0]
                veh_pos = traci.vehicle.getLanePosition(veh)
                distance = veh_pos
            except:
                distance = 0

            schedule_dev = traci.simulation.getTime() - self.last_dispatch_time
            dwell = traci.vehicle.getAccumulatedWaitingTime(veh)

            headway_dev = schedule_dev - self.target_headway

            features.extend([
                load,
                speed,
                distance,
                schedule_dev,
                dwell,
                headway_dev
            ])

        while len(features) < self.max_vehicles * 6:
            features.append(0)

        return np.array(features[:36])

    # --------------------------
    # 3️⃣ NETWORK-LEVEL (16)
    # --------------------------
    def get_network_features(self):

        vehicles = traci.vehicle.getIDList()

        total_co2 = sum(traci.vehicle.getCO2Emission(v) for v in vehicles)
        avg_speed = np.mean([traci.vehicle.getSpeed(v) for v in vehicles]) if vehicles else 0

        total_waiting = sum(traci.busstop.getPersonCount(s)
                            for s in traci.busstop.getIDList())

        edge_ids = traci.edge.getIDList()
        avg_density = np.mean([traci.edge.getLastStepVehicleNumber(e)
                               for e in edge_ids]) if edge_ids else 0

        congestion_ratio = avg_density / (len(edge_ids) + 1)

        bunching_index = abs(self.get_headway_deviation())

        features = [
            total_co2,
            avg_speed,
            total_waiting,
            avg_density,
            congestion_ratio,
            bunching_index
        ]

        # pad to 16
        while len(features) < 16:
            features.append(0)

        return np.array(features[:16])

    # ==========================
    # ACTION
    # ==========================
    def apply_action(self, action):
        # 1. Define the discrete action space (9 headway options x 3 dwell options = 27)
        headway_options = [-240, -180, -120, -60, 0, 60, 120, 180, 240]
        dwell_options = [0, 30, 60]

        # 2. Decode the 27 actions (0-26)
        headway_idx = action // 3
        dwell_idx = action % 3

        headway_shift = headway_options[headway_idx]
        dwell_extension = dwell_options[dwell_idx]

        current_time = traci.simulation.getTime()
        dispatch_time = self.last_dispatch_time + self.target_headway + headway_shift

        # 3. Check if current simulation time hits the calculated dispatch window
        if current_time >= dispatch_time:
            # Determine current route ("0" or "1")
            route_id = self.route_ids[self.direction_toggle]
            veh_id = f"bus_{route_id}_{int(current_time)}"

            try:
                # 4. Add the vehicle to the simulation
                traci.vehicle.add(
                    vehID=veh_id,
                    routeID=route_id,
                    typeID="bus"
                )
                
                # 5. Set the 'line' attribute so passengers in passengers.add.xml board
                traci.vehicle.setLine(veh_id, route_id)

                # 6. Apply Dwell Extension to the first stop of the route
                try:
                    # FIXED: Use route.getStops to get actual BusStop IDs (e.g., "0.0") 
                    # instead of lane IDs (e.g., "26006215#0_0")
                    all_stops = traci.vehicle.getStops(veh_id)
                    
                    if all_stops:
                        first_stop_id = all_stops[0].stoppingPlaceID
                        
                        # duration forces the bus to stay at the stop for at least this many seconds
                        traci.vehicle.setBusStop(
                            vehID=veh_id,
                            stopID=first_stop_id,
                            duration=dwell_extension
                        )
                except traci.TraCIException as stop_err:
                    print(f"DEBUG: Dwell adjustment failed for {veh_id}: {stop_err}")

                # 7. Update Environment State for toggling and headway tracking
                self.last_dispatch_time = current_time
                self.direction_toggle = 1 - self.direction_toggle
                
            except traci.TraCIException as dispatch_err:
                print(f"DEBUG: Dispatch Error for Route {route_id}: {dispatch_err}")

    # ==========================
    # REWARD
    # ==========================
    def compute_reward(self):

        total_wait = sum(traci.busstop.getPersonCount(s)
                         for s in traci.busstop.getIDList())

        total_emission = sum(traci.vehicle.getCO2Emission(v)
                             for v in traci.vehicle.getIDList())

        headway_penalty = abs(self.get_headway_deviation())

        # normalized components
        wait_norm = total_wait / 100
        emission_norm = total_emission / 10000
        headway_norm = headway_penalty / 600

        reward = -(0.5 * wait_norm +
                   0.3 * emission_norm +
                   0.2 * headway_norm)

        return reward

    def get_headway_deviation(self):
        current_time = traci.simulation.getTime()
        return current_time - self.last_dispatch_time - self.target_headway
