from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from news.models import NewsPage, NewsIndexPage
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.blocks import PageChooserBlock
#---------------------------------------------------------------
#bloque para una sección de autoridades
class AuthoritySectionBlock(blocks.StructBlock):
    """Bloque para una sección de autoridades"""
    title = blocks.CharBlock(required=True, label="Título de la sección")
    description = blocks.RichTextBlock(required=False, label="Descripción introductoria")
    display_style = blocks.ChoiceBlock(
        choices=[
            ('cards', 'Tarjetas (foto, nombre, cargo, bio)'),
            ('list', 'Lista simple (nombre, cargo)'),
            ('grid_cards', 'Tarjetas en cuadrícula'),
            ('horizontal_cards', 'Tarjetas horizontales'),
        ],
        default='cards',
        label="Estilo de visualización"
    )
    authorities = blocks.ListBlock(
        blocks.StructBlock([
            # Utiliza SnippetChooserBlock
            ('authority', SnippetChooserBlock('home.Authority', label="Autoridad")),
            ('highlight', blocks.BooleanBlock(required=False, label="Destacar")),
        ]),
        label="Autoridades",
        help_text="Selecciona las autoridades que pertenecen a esta sección"
    )
    
    class Meta:
        icon = "group"
        label = "Sección de autoridades"
        template = "home/blocks/authority_section_block.html"
#---------------------------------------------------------------
class CollegiateBodyBlock(blocks.StructBlock):
    """Bloque para cuerpos colegiados (Consejo, Asamblea)"""
    title = blocks.CharBlock(required=True, label="Título")
    
    # Cuerpo Docente
    faculty_titular = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Titular"),
        label="Docentes - Titulares"
    )
    faculty_suplente = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Suplente"),
        label="Docentes - Suplentes"
    )
    
    # Cuerpo Graduado
    graduate_titular = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Titular"),
        label="Graduados - Titulares"
    )
    graduate_suplente = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Suplente"),
        label="Graduados - Suplentes"
    )
    
    # Cuerpo Estudiantil (opcional)
    student_titular = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Titular"),
        label="Estudiantes - Titulares",
        required=False
    )
    student_suplente = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Suplente"),
        label="Estudiantes - Suplentes",
        required=False
    )

    # Cuerpo Nodocente
    graduate_titular = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Titular"),
        label="No docente - Titular",
        required=False
    )
    graduate_suplente = blocks.ListBlock(
        SnippetChooserBlock('home.Authority', label="Suplente"),
        label="No docente - Suplente",
        required=False
    )      
    
    class Meta:
        icon = "group"
        label = "Cuerpo colegiado"
        template = "home/blocks/collegiate_body_block.html"

          
#---------------------------------------------------------------
@register_snippet
class Authority(ClusterableModel):
    name = models.CharField(max_length=200, verbose_name="Nombre completo")
    position = models.CharField(max_length=200, verbose_name="Cargo")
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Foto"
    )
    bio = RichTextField(blank=True, verbose_name="Breve reseña")

    section = models.ForeignKey(
        'AuthoritySectionPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='authorities',
        verbose_name="Sección a la que pertenece"
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('position'),
        FieldPanel('photo'),
        FieldPanel('bio'),
        FieldPanel('section')
    ]

    class Meta:
        ordering = ['name']
        verbose_name = "Autoridad"
        verbose_name_plural = "Autoridades"

    def __str__(self):
        return f"{self.name} – {self.position}"


class AuthoritiesPage(Page):
    intro = RichTextField(blank=True, verbose_name="Texto introductorio")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    # Solo puede tener hijas de tipo AuthoritySectionPage
    subpage_types = ['home.AuthoritySectionPage']
    
    def get_context(self, request):
        context = super().get_context(request)
        # Esta línea busca las páginas hijas publicadas
        context['sections'] = self.get_children().live().specific()
        # Línea de depuración (opcional, para ver en consola)
        print(f"DEBUG: Secciones encontradas: {context['sections'].count()}")
        return context

    class Meta:
        verbose_name = "Página de autoridades"
        verbose_name_plural = "Páginas de autoridades"
#--------------------------------------------------------------------------------------
class AuthoritySectionPage(Page):
    """Página de sección de autoridades (ej: Decanato y Secretarías)"""
    intro = RichTextField(blank=True, verbose_name="Texto introductorio")
    
    # Campo para la imagen representativa de la sección
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagen representativa de la sección"
    )
    
    # StreamField para organizar las secciones 
    sections = StreamField([
        ('authority_section', AuthoritySectionBlock()),('collegiate_body', CollegiateBodyBlock()), 
    ], blank=True, use_json_field=True, verbose_name="Secciones")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('image'),  # ← Agrega el campo image aquí
        FieldPanel('sections'),
    ]
    
    parent_page_types = ['home.AuthoritiesPage']
    subpage_types = []
    
    class Meta:
        verbose_name = "Sección de autoridades"
        verbose_name_plural = "Secciones de autoridades"

#--------------------------------------------------------------------------------
class HeroSlide(blocks.StructBlock):
    """Bloque para cada slide del carrusel"""
    image = ImageChooserBlock(required=True, label="Imagen de fondo")
    title = blocks.CharBlock(required=True, label="Título principal", max_length=100)
    subtitle = blocks.TextBlock(required=False, label="Subtítulo o descripción", max_length=200)
    button_text = blocks.CharBlock(required=False, label="Texto del botón", max_length=50)
    button_link = blocks.URLBlock(required=False, label="Enlace del botón")
    
    class Meta:
        icon = "image"
        label = "Slide del carrusel"
        template = "home/blocks/hero_slide.html"
# blocks.py

class CardBlock(blocks.StructBlock):
    """Tarjeta de acceso rápido - toda la tarjeta es cliqueable"""
    icon = blocks.CharBlock(
        required=True,
        label="Icono (Bootstrap icon)",
        help_text="Ejemplo: bi-pencil-square, bi-mortarboard, etc."
    )
    title_line1 = blocks.CharBlock(
        required=True,
        label="Primera línea del título",
        max_length=50
    )
    title_line2 = blocks.CharBlock(
        required=True,
        label="Segunda línea del título",
        max_length=50
    )
    link_page = PageChooserBlock(
        required=False,
        label="Página interna de destino"
    )
    external_link = blocks.URLBlock(
        required=False,
        label="Enlace externo"
    )
    gradient_class = blocks.ChoiceBlock(
        choices=[
            ('custom-grad-1', 'Gradiente 1'),
            ('custom-grad-2', 'Gradiente 2'),
            ('custom-grad-3', 'Gradiente 3'),
            ('custom-grad-4', 'Gradiente 4'),
            ('custom-grad-5', 'Gradiente 5'),
            ('custom-grad-6', 'Gradiente 6'),
        ],
        required=True,
        label="Color de la tarjeta"
    )

    class Meta:
        icon = "card"
        label = "Tarjeta de acceso rápido"
        template = "home/blocks/card_block.html"

class InstitutionalBlock(blocks.StructBlock):
    """Bloque para la sección institucional"""
    title = blocks.CharBlock(required=True, label="Título de la sección", default="Institucional")
    text_line1 = blocks.TextBlock(required=True, label="Primer párrafo")
    text_line2 = blocks.TextBlock(required=False, label="Segundo párrafo")
    button_text = blocks.CharBlock(required=False, label="Texto del botón", default="Conocer más")
    button_link = blocks.URLBlock(required=False, label="Enlace del botón")
    image = ImageChooserBlock(required=True, label="Imagen institucional")
    
    class Meta:
        icon = "image"
        label = "Sección institucional"
        template = "home/blocks/institutional_block.html"


class MetricsBlock(blocks.StructBlock):
    """Bloque para las métricas"""
    metric1_number = blocks.CharBlock(required=True, label="Número 1", default="10")
    metric1_label = blocks.CharBlock(required=True, label="Etiqueta 1", default="carreras de grado")
    metric2_number = blocks.CharBlock(required=True, label="Número 2", default="12")
    metric2_label = blocks.CharBlock(required=True, label="Etiqueta 2", default="carreras de posgrado")
    description = blocks.TextBlock(required=True, label="Texto descriptivo")
    button_text = blocks.CharBlock(required=False, label="Texto del botón", default="INSCRIBIRSE")
    button_link = blocks.URLBlock(required=False, label="Enlace del botón")
    
    class Meta:
        icon = "table"
        label = "Sección de métricas"
        template = "home/blocks/metrics_block.html"


class HomePage(Page):
    """Página de inicio con todas las secciones editables"""
     # Hero / Carrusel
    carousel_slides = StreamField(
        [('slide', HeroSlide())],
        blank=True,
        use_json_field=True,
        help_text="Agregá los slides que quieras mostrar en el carrusel principal"
    )
    
    # Tarjetas de acceso rápido
    cards = StreamField(
        [('card', CardBlock())],
        blank=True,
        use_json_field=True,
        help_text="Agregá las tarjetas de acceso rápido"
    )
    
    # Sección institucional
    institutional_section = StreamField(
        [('institutional', InstitutionalBlock())],
        blank=True,
        use_json_field=True,
        help_text="Sección institucional"
    )
    
    # Sección de métricas
    metrics_section = StreamField(
        [('metrics', MetricsBlock())],
        blank=True,
        use_json_field=True,
        help_text="Sección de métricas"
    )
    
    # Paneles de administración
    content_panels = Page.content_panels + [
        FieldPanel('carousel_slides'),
        FieldPanel('cards'),
        FieldPanel('institutional_section'),
        FieldPanel('metrics_section'),
    ]
    subpage_types = [
        'home.AuthoritiesPage',
        'news.NewsIndexPage',
        'courses.CareerIndexPage',
        'departments.DepartmentsIndexPage',
        # ... otros índices que tengas
    ]
    # Especificamos el template a usar
    template = "home/home_page.html"
    

    def get_context(self, request):
        context = super().get_context(request)        
        context['latest_news'] = NewsPage.objects.live().order_by('-date')[:3]
        return context