import os
import subprocess

def install():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(root_dir)
    rnaview_folder = os.path.join(root_dir, "RNAView-master")
    command = f'setx RNAVIEW "{rnaview_folder}"'
    second_command = 'setx PATH "%RNAVIEW%\\bin;%PATH%"'
    subprocess.run(command, check=True)
    subprocess.run(second_command, check=True)

if __name__ == "__main__":
    install()
