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


def figures_dir(create=False):
    path = source_dir().joinpath('figures')
    if not create:
        if path.is_dir():
            return path
        raise Exception(f"No existe directorio de figuras LaTeX en '{source_dir()}'")
    else:
        path.mkdir(exist_ok=True)
        return path


def generated_img_path(filename, create_dirs=False):
    return generated_img_dir(create_dirs=create_dirs).joinpath(filename)


def figure_path(filename, create_dirs=False):
    return figures_dir(create=create_dirs).joinpath(filename)


def write_figure_content_tex(nombre_imagen, caption):
    latex_code = f'\\contenidofigura{{{nombre_imagen}}}{{{caption}}}'
    path = figure_path(f"{nombre_imagen.split('.')[0]}-content.tex", create_dirs=True)
    path.write_text(latex_code, encoding='utf-8')


def write_figure_tex(nombre_imagen, caption):
    latex_code = f'\\figura{{{nombre_imagen}}}{{{caption}}}'
    path = figure_path(f"{nombre_imagen.split('.')[0]}.tex", create_dirs=True)
    path.write_text(latex_code, encoding='utf-8')
