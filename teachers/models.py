from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel

class CalendarBlock(blocks.StructBlock):
    """Bloque para mostrar un calendario o agenda (puede ser un embed de Google Calendar)"""
    title = blocks.CharBlock(required=False, label="Título")
    embed_url = blocks.URLBlock(required=True, label="URL del calendario (embed)")
    height = blocks.IntegerBlock(default=600, label="Altura en píxeles")

    class Meta:
        icon = "date"
        label = "Calendario"
        template = "teachers/blocks/calendar_block.html"

class LinkCardBlock(blocks.StructBlock):
    """Tarjeta de enlace con ícono, título y descripción"""
    title = blocks.CharBlock(required=True, label="Título")
    description = blocks.TextBlock(required=False, label="Descripción")
    link_url = blocks.URLBlock(required=True, label="URL")
    icon_class = blocks.CharBlock(required=False, label="Clase del ícono (ej: bi bi-calendar)", default="bi bi-link")

    class Meta:
        icon = "link"
        label = "Tarjeta de enlace"
        template = "teachers/blocks/link_card_block.html"

class DocumentLinkBlock(blocks.StructBlock):
    """Enlace a documento descargable"""
    title = blocks.CharBlock(required=True, label="Título del documento")
    document = DocumentChooserBlock(required=True, label="Archivo PDF/Word")

    class Meta:
        icon = "doc-full"
        label = "Documento descargable"
        template = "teachers/blocks/document_link_block.html"

class TeachersPage(Page):
    """Página informativa para docentes (contenido editable por bloques)"""
    intro = RichTextField(blank=True, verbose_name="Texto introductorio")

    content = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='pilcrow', label='Texto enriquecido')),
        ('link_cards', blocks.ListBlock(LinkCardBlock(), icon='th-large', label='Tarjetas de enlaces')),
        ('document_list', blocks.ListBlock(DocumentLinkBlock(), icon='doc-full', label='Lista de documentos')),
        ('calendar', CalendarBlock()),
        ('image_gallery', blocks.ListBlock(ImageChooserBlock(), icon='image', label='Galería de imágenes')),
        ('separator', blocks.StructBlock([], icon='horizontalrule', label='Separador')),
    ], blank=True, use_json_field=True, verbose_name="Contenido principal")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('content'),
    ]

    # Restringir qué páginas pueden ser hijas (ninguna, porque es una página terminal)
    subpage_types = []

    class Meta:
        verbose_name = "Página de Docentes"
        verbose_name_plural = "Páginas de Docentes"

