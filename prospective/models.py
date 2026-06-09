from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel

class HeroImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Imagen principal")
    class Meta:
        icon = "image"
        label = "Imagen de encabezado"
        template = "prospective/blocks/hero_image_block.html"

class StepsListBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, label="Título")
    steps = blocks.ListBlock(
        blocks.StructBlock([
            ('step_title', blocks.CharBlock(label="Título del paso")),
            ('description', blocks.RichTextBlock(label="Descripción")),
            ('links', blocks.ListBlock(
                blocks.StructBlock([
                    ('text', blocks.CharBlock(label="Texto del enlace")),
                    ('url', blocks.URLBlock(label="URL")),
                ]), required=False, label="Enlaces"
            )),
        ]), label="Pasos"
    )
    class Meta:
        icon = "list-ul"
        label = "Lista de pasos"
        template = "prospective/blocks/steps_list_block.html"

class DocumentsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Título")
    documents = blocks.ListBlock(
        blocks.StructBlock([
            ('title', blocks.CharBlock(label="Título del documento")),
            ('file', DocumentChooserBlock(label="Archivo")),
        ]), label="Documentos"
    )
    class Meta:
        icon = "doc-full"
        label = "Lista de documentos"
        template = "prospective/blocks/documents_block.html"

class TableBlock(blocks.StructBlock):
    content = blocks.RichTextBlock(label="Contenido de la tabla", help_text="Usa el editor para crear una tabla HTML")
    class Meta:
        icon = "table"
        label = "Tabla"
        template = "prospective/blocks/table_block.html"

class TabsBlock(blocks.StructBlock):
    tabs = blocks.ListBlock(
        blocks.StructBlock([
            ('tab_title', blocks.CharBlock(label="Título de la pestaña")),
            ('tab_content', blocks.RichTextBlock(label="Contenido")),
        ]), label="Pestañas"
    )
    class Meta:
        icon = "folder-open"
        label = "Pestañas (tabs)"
        template = "prospective/blocks/tabs_block.html"

class ContactBlock(blocks.StructBlock):
    emails = blocks.ListBlock(blocks.EmailBlock(), label="Correos electrónicos")
    class Meta:
        icon = "mail"
        label = "Contactos"
        template = "prospective/blocks/contact_block.html"

class ProspectivePage(Page):
    intro = RichTextField(blank=True, verbose_name="Texto introductorio")
    content = StreamField([
        ('hero_image', HeroImageBlock()),
        ('rich_text', blocks.RichTextBlock(icon='pilcrow', label='Texto enriquecido')),
        ('steps_list', StepsListBlock()),
        ('documents', DocumentsBlock()),
        ('table', TableBlock()),
        ('tabs', TabsBlock()),
        ('contact', ContactBlock()),
        ('separator', blocks.StructBlock([], icon='horizontalrule', label='Separador')),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('content'),
    ]

    parent_page_types = ['home.HomePage']   # hija de Home
    subpage_types = []

    class Meta:
        verbose_name = "Página de Ingresantes"
        verbose_name_plural = "Páginas de Ingresantes"
