import pathlib as pl

ROOT_PATH = pl.Path(__file__).parent
SRC_PATH = ROOT_PATH.joinpath('src')
GENERATED_IMAGES_PATH = SRC_PATH.joinpath('images').joinpath('generated')


def _make_generated_dir():
    # asegurar existencia de directorios
    gen_dir = GENERATED_IMAGES_PATH
    gen_dir.mkdir(exist_ok=True, parents=True)
    return gen_dir


def generated_img_path(filename):
    return _make_generated_dir().joinpath(filename)
