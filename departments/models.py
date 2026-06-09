from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel

class DepartmentsIndexPage(Page):
    """Página índice que lista todos los departamentos."""
    intro = RichTextField(blank=True, null=True, help_text="Texto de introducción para la página de departamentos.")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    # Aquí se define que solo se pueden crear páginas de tipo 'DepartmentPage' como hijas.
    subpage_types = ['departments.DepartmentPage']

    def get_context(self, request):
        """Añade la lista de páginas hijas (departamentos) al contexto de la plantilla."""
        context = super().get_context(request)
        # Obtiene las páginas hijas, públicas, y ordenadas por título.
        # El método .specific() convierte las páginas genéricas a su tipo específico (DepartmentPage)
        # para poder acceder a todos sus campos personalizados.
        context['departments'] = self.get_children().live().specific().order_by('title')
        return context

    class Meta:
        verbose_name = "Página de Índice de Departamentos"
        verbose_name_plural = "Páginas de Índice de Departamentos"



# ... (imports)

class HeroInfoBlock(blocks.StructBlock):
    """Bloque de presentación con título, descripción e imagen."""
    title = blocks.CharBlock(required=False, label="Título de sección")
    description = blocks.RichTextBlock(required=True, label="Descripción principal")
    image = ImageChooserBlock(required=False, label="Imagen lateral o de fondo")

    class Meta:
        icon = "image"
        label = "Presentación"
        template = "departments/blocks/hero_info_block.html"


class LinkItemBlock(blocks.StructBlock):
    """Un enlace individual con ícono y descripción opcional."""
    link_text = blocks.CharBlock(required=True, label="Texto del enlace")
    link_url = blocks.URLBlock(required=True, label="URL")
    icon_class = blocks.CharBlock(required=False, label="Clase CSS del ícono (ej: bi bi-file-pdf)", default="bi bi-link")

    class Meta:
        icon = "link"
        label = "Enlace simple"
        template = "departments/blocks/link_item_block.html"


class LinksGroupBlock(blocks.StructBlock):
    """Grupo de enlaces (como los que aparecen en el ejemplo: Consultas, Incumbencias, Planes, etc.)"""
    group_title = blocks.CharBlock(required=False, label="Título del grupo (opcional)")
    links = blocks.ListBlock(LinkItemBlock(), label="Lista de enlaces")

    class Meta:
        icon = "list-ul"
        label = "Grupo de enlaces"
        template = "departments/blocks/links_group_block.html"


class NewsListBlock(blocks.StructBlock):
    """Lista de novedades propias del departamento (no las globales)."""
    title = blocks.CharBlock(default="Novedades", label="Título de la sección")
    max_items = blocks.IntegerBlock(default=3, min_value=1, max_value=10, label="Cantidad de novedades a mostrar")

    class Meta:
        icon = "date"
        label = "Novedades del departamento"
        template = "departments/blocks/news_list_block.html"


class DocumentListBlock(blocks.StructBlock):
    """Lista de documentos descargables (plan de estudio, formularios, etc.)."""
    title = blocks.CharBlock(default="Documentos útiles", label="Título")
    documents = blocks.ListBlock(
        blocks.StructBlock([
            ("title", blocks.CharBlock(label="Título del documento")),
            ("document", DocumentChooserBlock(label="Archivo")),
        ]),
        label="Documentos"
    )

    class Meta:
        icon = "doc-full"
        label = "Lista de documentos"
        template = "departments/blocks/document_list_block.html"


class DepartmentPage(Page):
    """Página de un departamento específico."""
    
    # Campos fijos (siempre presentes)
    contacto_email = models.EmailField(blank=True, verbose_name="Email de contacto")
    telefono = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    
    # StreamField para contenido principal (ordenable y flexible)
    content = StreamField([
        ('hero_info', HeroInfoBlock()),
        ('rich_text', blocks.RichTextBlock(icon='pilcrow', label='Texto enriquecido')),
        ('links_group', LinksGroupBlock()),
        ('document_list', DocumentListBlock()),
        ('news_list', NewsListBlock()),
        ('image_gallery', blocks.ListBlock(ImageChooserBlock(), icon='image', label='Galería de imágenes')),
        ('quote', blocks.BlockQuoteBlock(icon='openquote', label='Cita')),
        # Puedes agregar más bloques según necesites
    ], blank=True, use_json_field=True, verbose_name="Contenido de la página")

    content_panels = Page.content_panels + [
        FieldPanel('contacto_email'),
        FieldPanel('telefono'),
        FieldPanel('content'),
    ]

    # Restringir que solo pueda ser creada bajo DepartmentsIndexPage
    parent_page_types = ['departments.DepartmentsIndexPage']

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"