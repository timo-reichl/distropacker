from argparse import ArgumentParser
from pathlib import Path

from distropacker.package import DistroBaseNotFoundError
from distropacker.package import DistroNotFoundError
from distropacker.package import package_manager


# distropacker -b <build_dir> -d <distro list> --dependencies <dependencies_list> --tag <tag> --force <true/false>
arg_parser = ArgumentParser("distropacker")
# TODO: Figure out a uniform way to add build time dependencies (mapping files?)
arg_parser.add_argument("--dependencies", type=str, nargs="+", help="Build time dependencies")
arg_parser.add_argument("-t", "--tag", type=str, help="Docker image tag")
arg_parser.add_argument("-f", "--force", action="store_true", help="Force rebuild of image")

args_required = arg_parser.add_argument_group("required")
args_required.add_argument("-b", "--build-dir", type=str, required=True)
args_required.add_argument("-d", "--distro-list", type=str, nargs="+", required=True)

args = arg_parser.parse_args()


for distro in args.distro_list:
    try:
        package = package_manager.get(distro, f"{Path(args.build_dir).joinpath(distro.lower())}")
        package.build([] if args.dependencies is None else args.dependencies, tag=args.tag, force=args.force)

    except DistroNotFoundError as error:
        print(f"Distro {error.name} could not be found.")
        print("Here's a list:")
        print("\n".join([f" {distro}" for distro in package_manager.distros]))

    except DistroBaseNotFoundError as error:
        print(f"Distro base {error.name} could not be found.")
        print("Here's a list:")
        print("\n".join([f" {distro}" for distro in package_manager.bases]))
