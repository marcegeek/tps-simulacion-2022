import pathlib as pl

DIRECTORIOS = ['presentacion', 'presentation']


def source_dir():
    for d in DIRECTORIOS:
        path = pl.Path(d).joinpath('src')
        if path.is_dir():
            return path
    raise Exception(f"No existe directorio presentación LaTeX en '{pl.Path('.').absolute()}'")


def image_dir(create=False):
    path = source_dir().joinpath('images')
    if not create:
        if path.is_dir():
            return path
        raise Exception(f"No existe directorio de imágenes LaTeX en '{source_dir()}'")
    else:
        path.mkdir(exist_ok=True)
        return path


def generated_img_dir(create_dirs=False):
    path = image_dir(create=create_dirs).joinpath('generated')
    if not create_dirs:
        if path.is_dir():
            return path
        raise Exception(f"No existe directorio de imágenes LaTeX generadas en '{image_dir()}'")
    else:
        path.mkdir(exist_ok=True, parents=True)
        return path


def generated_img_path(filename, create_dirs=False):
    return generated_img_dir(create_dirs=create_dirs).joinpath(filename)
