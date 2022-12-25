from collections import defaultdict
from pathlib import Path
import re
import typing

# Regex to detect numbers (at the beginning of a line)
number_regex = re.compile(r"[0-9]+")


def generate_inputs(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
) -> typing.Iterable[str]:
    """Generate lines from the given input file.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing commands and output.

    Yields
    ------
    input_line: str
        Single line of file content, either a command or part of command output.
    """
    with open(filepath, "r") as inputs_file:
        for line in inputs_file:
            yield line.strip()


def directory_sizes(
    input_lines, root_directory_name: str = "/"
) -> typing.Dict[str, int]:
    """Determine cummulative directory sizes (including subdirectories) for
       all directories processed in the commands.

    Parameters
    ----------
    input_lines : typing.Iterable[str]
        Input lines that could contain commands or (partial) command output.

    Returns
    -------
    directory_size_mapping: typing.Dict[str, int]
        Mapping of directory paths (as strings) to cummulative filesize in
        this directory (and all subdirectories).
    """
    # Directory sizes start at 0.
    total_directory_sizes = defaultdict(int)

    # Manage filepath as a stack, popping items to move up a directory
    # and appending items to navigate into subdirectories.
    current_filepath = [root_directory_name]

    for line in input_lines:
        if line.startswith("$ ls"):  # Ignore any ls commands.
            continue
        elif line.startswith("$ cd"):
            if line == f"$ cd {root_directory_name}":
                current_filepath = [root_directory_name]
            elif line == "$ cd ..":
                _ = current_filepath.pop()
            else:
                *_, directory_name = line.split()
                current_filepath.append(directory_name)
        elif re.match(pattern=number_regex, string=line):
            file_size, *_ = line.split()
            file_size = int(file_size)

            # NOTE: Traverse the stack to process parent directories, add
            # the file size to each parent directory.
            for i in range(len(current_filepath)):
                directory_path = "/".join(current_filepath[: i + 1]).replace("//", "/")
                total_directory_sizes[directory_path] += file_size
        else:
            continue

    return total_directory_sizes


def part_1(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    directory_size_threshold: int = 100_000,
    root_directory_name: str = "/",
) -> int:
    """Determine sum of directory sizes of all directories with size under the threshold.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing commands and output.
    directory_size_threshold : int, optional
        Threshold to apply to directory sizes before computing the sum.
        Default: `100_000`.
    root_directory_name: str, optional
        Root directory to start computing directory sizes from.
        Default: `"/"`.

    Returns
    -------
    directory_size_sum: int
        Sum of directory sizes of all directories with size under `directory_size_threshold`.
    """
    relevant_directories = [
        (directory_name, directory_size)
        for (directory_name, directory_size) in directory_sizes(
            input_lines=generate_inputs(filepath=filepath),
            root_directory_name=root_directory_name,
        ).items()
        if directory_size <= directory_size_threshold
    ]
    return sum(directory_size for _, directory_size in relevant_directories)


def part_2(
    filepath: Path = Path(__file__).parent.parent.joinpath("inputs.txt"),
    total_disk_space: int = 70_000_000,
    needed_disk_space: int = 30_000_000,
    root_directory_name: str = "/",
) -> int:
    """Determine directory with minimal size to delete to free up needed disk space.

    Parameters
    ----------
    filepath : pathlib.Path, optional
        Input file containing commands and output.
    total_disk_space: int, optional
        Total available disk space. Default: `70_000_000`
    needed_disk_space: int, optional
        Disk space to free up. Default: `30_000_000`
    root_directory_name: str, optional
        Root directory to start computing directory sizes from.
        Default: `"/"`.

    Returns
    -------
    min_directory_size: int
        Size of minimal size directory to delete to free up `needed_disk_space`
        on a disk with `total_disk_space` space.
    """
    if needed_disk_space > total_disk_space:
        raise ValueError("Can't free up more space than is available in total..")

    all_directory_sizes = directory_sizes(
        input_lines=generate_inputs(filepath=filepath),
        root_directory_name=root_directory_name,
    )

    space_to_free_up = (
        all_directory_sizes[root_directory_name] + needed_disk_space - total_disk_space
    )

    relevant_directories = [
        (directory_name, directory_size)
        for directory_name, directory_size in all_directory_sizes.items()
        if directory_size >= space_to_free_up
    ]
    return min(directory_size for _, directory_size in relevant_directories)


def main():
    print("Part 1:", part_1())
    print("Part 1:", part_2())


if __name__ == "__main__":
    main()
