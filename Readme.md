# Conda Environment Management for the Fly Me to the Moon Music Project

## Creating the Environment

1. Create a new Conda environment:
   ```
   conda create --name music python=3.12
   ```

2. Activate the new environment:
   ```
   conda activate music
   ```

3. Install required packages:
   ```
   conda install numpy
   conda install conda-forge::pygame
   ```
   Using `conda-forge::pygame` ensures you're installing pygame from the conda-forge channel, which often has more up-to-date packages.

## Exporting the Environment

After setting up your environment and installing all necessary packages, you can export it:

1. Activate the environment if it's not already active:
   ```
   conda activate music
   ```

2. Export the environment to a YAML file:
   ```
   conda env export > music_environment.yml
   ```

This creates a `music_environment.yml` file that contains all the information about your environment and its dependencies.

## Recreating the Environment on Another Computer

To recreate the environment on another computer:

1. Copy the `music_environment.yml` file to the new computer.

2. Open a terminal or command prompt on the new computer.

3. Create the environment from the YAML file:
   ```
   conda env create -f music_environment.yml
   ```

4. Activate the newly created environment:
   ```
   conda activate music
   ```

## Alternative: Creating a Minimal Environment File

If you want to create a minimal environment file that only includes the packages you explicitly installed:

1. Create a new file named `environment.yml` with the following content:
   ```yaml
   name: music
   channels:
     - conda-forge
     - defaults
   dependencies:
     - python=3.12
     - numpy
     - pygame
   ```

2. Create the environment from this file:
   ```
   conda env create -f environment.yml
   ```

This method allows for easier version control and sharing, as it only specifies the main dependencies and allows Conda to resolve sub-dependencies.

Remember to always activate the environment before working on your project:
```
conda activate music
```

And deactivate when you're done:
```
conda deactivate
```




# Installing SCAMP in Conda

1. Open your terminal or command prompt.

2. Create a new Conda environment (let's call it 'scamp-env'):
   ```
   conda create -n scamp-env python=3.9
   ```

3. Activate the new environment:
   ```
   conda activate scamp-env
   ```

4. Install pip in the Conda environment (if not already installed):
   ```
   conda install pip
   ```

5. Use pip to install SCAMP:
   ```
   pip install scamp
   ```

6. (Optional) If you want to use MIDI output, you might need to install FluidSynth:
   - On macOS: `brew install fluid-synth`
   - On Ubuntu: `sudo apt-get install fluidsynth`
   - On Windows: Download and install FluidSynth from its official website

Now you have SCAMP installed in your Conda environment!