import os
import re
import numpy as np

def measure_transfer_and_pto_count(
    ptos_list: list[list[list[Transfer]]],
    transition_start: int = 0,
    transition_end: int = -1,
) -> tuple[int, int]:
    transfer_count = 0
    pto_count = 0
    if transition_end == -1:
        transition_end = len(ptos_list)
    for i in range(len(ptos_list)):
        # print(">>> Transition #", i)
        if i >= transition_start and i <= transition_end:
            pto_count += len(ptos_list[i])
        for pto in ptos_list[i]:
            # print([transfer.qbit_id for transfer in pto])
            transfer_count += len(pto)
    return transfer_count, pto_count


def measure_total_distance(
    transfers_list_per_transition: list[list[list[Transfer]]],
) -> float:
    total_distance = 0.0
    for transfers_list in transfers_list_per_transition:
        for transfers in transfers_list:
            for transfer in transfers:
                total_distance += np.sqrt(
                    (transfer.start.x - transfer.end.x) ** 2
                    + (transfer.start.y - transfer.end.y) ** 2
                )
    return total_distance

VEC_PATTERN = re.compile(r"\(([^)]+)\)")

class Vec:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def copy(self):
        return Vec(self.x, self.y)

class Transfer:
    def __init__(
        self,
        start: Vec = Vec(-1.0, -1.0),
        end: Vec = Vec(-1.0, -1.0),
        qbit_id: int = -1,
    ) -> None:
        self.start: Vec = start
        self.end: Vec = end
        self.qbit_id: int = qbit_id


def parse_vec(s):
    x, y = map(float, s.split(","))
    return Vec(x, y)


def extract_vecs(text):
    return [parse_vec(v) for v in VEC_PATTERN.findall(text)]

def load_file(filename):
    with open(filename, "r") as f:
        content = f.read().strip()

    # Split start positions from transitions
    parts = re.split(r"\n\s*\n\s*\n", content, maxsplit=1)
    if len(parts) != 2:
        raise ValueError("Invalid file format")

    position_part, transition_part = parts

    # ---- Parse positions ----
    start_positions = {}
    for line in position_part.splitlines():
        # start <id> (x, y)
        tokens = line.split(maxsplit=2)
        qbit_id = int(tokens[1])
        vec = extract_vecs(tokens[2])[0]
        start_positions[qbit_id] = vec
    max_id = max(start_positions)
    start_positions_list = [
        start_positions[i] if i in start_positions else Vec(float("nan"), float("nan"))
        for i in range(max_id + 1)
    ]
    # ---- Parse transitions ----
    transitions = []

    # Split blocks (more tolerant)
    transition_blocks = re.split(r"\n\s*\n\s*\n\s*\n", transition_part.strip())

    for block in transition_blocks:
        transfers_list = []

        groups = re.split(r"\n\s*\n", block.strip())
        for group in groups:
            transfers = []

            for line in group.splitlines():
                parts = line.split(maxsplit=1)
                qbit_id = int(parts[0])

                vecs = extract_vecs(parts[1])
                if len(vecs) != 2:
                    raise ValueError(f"Invalid vector format: {line}")

                transfers.append(Transfer(vecs[0], vecs[1], qbit_id))

            transfers_list.append(transfers)

        transitions.append(transfers_list)

    return transitions, start_positions_list

def run():
    folder = 'mappings'
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    for file in files:
        print('Analizing ', file)
        input('Press any key...')
        print(file)
        ptos_list, start_positions = load_file(str('mappings/' + str(file)))
        for pos in start_positions:
            print(pos.x, pos.y)
        for transfers_list in ptos_list:
            print("\n\n\nTransition")
            for transfers in transfers_list:
                print("\nPTO")
                for transfer in transfers:
                    print(
                        transfer.qbit_id,
                        transfer.start.x,
                        transfer.start.y,
                        transfer.end.x,
                        transfer.end.y,
                    )
        print("Total transfer/pto count:", measure_transfer_and_pto_count(ptos_list))
        print("Total distance:", measure_total_distance(ptos_list))
        input('Press any key...')
        print('\n\n\n\n\n\n\n')

run()
