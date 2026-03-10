1. **Analyze Requirements and Resources**:
   - The project aims to simulate post-disaster repair scheduling for a coupled traffic-power network.
   - We need to write Python code to model the network, simulate 4 strategies (S1 to S4), and collect metrics (AUC, Makespan, Load Restored).
   - Use `wandb` to log the experiments.
   - Generate local plots (LSD curve, AUC/Makespan bar charts), upload them to `imgbb`, and produce a final `report.md`.

2. **Develop the Simulation Code**:
   - Write a Python simulator (`simulator.py`) including:
     - Graph definitions for road and power layers.
     - Event-driven simulation core (handling movement, repair, and state transitions).
     - Implement the 4 strategies:
       - S1 (Road first, then Power)
       - S2 (Parallel Road and Power)
       - S3 (Helicopter/Aerial support)
       - S4 (Combined ground and aerial)
   - The simulator will track the `load_restored` over time for each strategy.

3. **Run Experiments and Log to Wandb**:
   - Create an experiment script (`run_experiments.py`) that initializes `wandb`, runs the 4 strategies, and logs the load curves, AUC, and Makespan.

4. **Generate Visualizations and Upload**:
   - Use `matplotlib` to generate the LSD curve and AUC bar chart.
   - Write a script to upload these local images to the provided `imgbb` API.
   - Retrieve the public URLs of the uploaded images.

5. **Complete pre-commit steps**:
   - Ensure proper testing, verification, review, and reflection are done.

6. **Draft the Final Report**:
   - Create `report.md` detailing the background, modeling, strategies, and experimental results.
   - Embed the image URLs obtained from `imgbb` into the report.
