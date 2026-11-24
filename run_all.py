"""Run steps 2 to 4 for both sample designs. Progress is printed (redirect it to a log if you like).

    python run_all.py              # build, then walk forward and fixed split: train + evaluate
    python run_all.py --skip_build
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [["pipeline/02_build_dataset.py"],
         ["pipeline/03_train.py"], ["pipeline/04_evaluate.py"],
         ["pipeline/03_train.py", "--fixed"], ["pipeline/04_evaluate.py", "--fixed"]]
# a quick check that numpy and torch load and an LSTM runs, before hours of training start
TORCH_CHECK = ("import numpy, torch; print('numpy', numpy.__version__, 'torch', torch.__version__); "
               "print('lstm ok', torch.nn.LSTM(3, 4)(torch.zeros(2, 5, 3))[0].shape)")


def main():
    steps = STEPS[1:] if "--skip_build" in sys.argv else STEPS
    print("python", sys.version.split()[0], sys.executable, flush=True)
    r = subprocess.run([sys.executable, "-X", "faulthandler", "-c", TORCH_CHECK])
    print("torch check return code", r.returncode, flush=True)

    for step in steps:
        print("===", " ".join(step), flush=True)
        code = subprocess.run([sys.executable, "-u", "-X", "faulthandler", *step], cwd=ROOT).returncode
        if code != 0:
            print("=== FAILED at", " ".join(step), "return code", code, flush=True)
            sys.exit(1)
    print("=== ALL DONE", flush=True)


if __name__ == "__main__":
    main()
