import jinja2
import pdfkit

def crear_pdf(ruta_template, info, rutacss=''):
    nombre_template = ruta_template.split('\\')[-1]  # Ajustado para dividir por '\\' en rutas de Windows
    ruta_template = ruta_template.replace(nombre_template, '')
    
    options = {'page-size': 'Letter',
               'margin-top': '0.05in',  # Corregido el nombre de la propiedad de margen
               'margin-right': '0.05in',
               'margin-bottom': '0.05in',  # Corregido el nombre de la propiedad de margen
               'margin-left': '0.05in',
               'encoding': 'UTF-8'}
    
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
 # Ajustada la ruta

    env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ruta_template),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
    auto_reload=True,
    cache_size=0,  # Disable the cache
)



    template = env.get_template(nombre_template)
    html = template.render(info)
    ruta_salida = 'C:\\Users\\Mari\\OneDrive\\Escritorio\\pdf\\aplicacion\\pdf.pdf'
    pdfkit.from_string(html, ruta_salida, options=options, configuration=config)

if __name__ == "__main__":
    ruta_template = 'C:\\Users\\Mari\\OneDrive\\Escritorio\\Brisas del Este\\aplicacion\\templates\\pdf.html'
    info = {}
    crear_pdf(ruta_template, info)
