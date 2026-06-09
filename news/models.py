from django.db import models
from django.utils import timezone
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel

class NewsIndexPage(Page):
    """Página que lista todas las noticias"""
    intro = models.TextField(blank=True, help_text="Texto introductorio de la sección noticias")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        # Obtener todas las noticias publicadas, ordenadas por fecha (más reciente primero)
        context['news_pages'] = NewsPage.objects.live().order_by('-date')
        
        news_index = NewsIndexPage.objects.live().first()
        context['news_index_url'] = news_index.url if news_index else '#'    
    
        return context
    
    class Meta:
        verbose_name = "Página de noticias"
        verbose_name_plural = "Páginas de noticias"


class NewsPage(Page):
    """Página individual de una noticia"""
    date = models.DateField(default=timezone.now, verbose_name="Fecha de publicación")
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagen destacada"
    )
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title", icon="title", label="Título")),
        ('paragraph', blocks.RichTextBlock(icon="pilcrow", label="Párrafo")),
        ('image', ImageChooserBlock(icon="image", label="Imagen")),
        ('quote', blocks.BlockQuoteBlock(icon="openquote", label="Cita")),
    ], blank=True, use_json_field=True, verbose_name="Contenido")
    
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('featured_image'),
        FieldPanel('body'),
    ]
    
    parent_page_types = ['news.NewsIndexPage']
    
    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"