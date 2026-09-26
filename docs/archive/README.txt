BloodTap - current complete executable simulator baseline for VS Code

FILES
- simulator.py       Main simulator engine.
- economy_data.json  Economy/producer/upgrade data required by simulator.py.
- garden_data.json   Garden catalog data required by simulator.py.
- test_core.py       Core verification suite for this executable baseline.

RUN IN VS CODE
1. Open this folder in VS Code.
2. Make sure Python 3 is installed and selected as the interpreter.
3. Open a terminal in this folder.
4. Run: python test_core.py
5. For simulator experimentation, import from simulator.py or run your study scripts from this same folder.

IMPORTANT VERSION NOTE
This package is the newest COMPLETE EXECUTABLE simulator source currently recoverable as one coherent baseline. Later BloodTap engineering milestones v0.19-v0.28 contain additional verified rule/test work, but their fully merged simulator.py was not persisted as a complete source file. Those later milestone tests must not be presented as runnable against this package until they are merged into simulator.py. This package is intentionally labeled accurately rather than pretending the later test-only milestones are already integrated.
