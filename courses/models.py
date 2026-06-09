from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.models import Document
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet

# Modelo para el plan de estudios
class SyllabusBlock(blocks.StructBlock):
    """Bloque para cada plan de estudio"""
    year = blocks.CharBlock(required=True, max_length=10, label="Año",
                            help_text="Ej: 2003, 2010, 2024")
    title = blocks.CharBlock(required=False, max_length=100, label="Título personalizado",
                            help_text="Opcional. Ej: 'Plan anterior', 'Plan vigente'")
    file = DocumentChooserBlock(required=True, label="Archivo PDF",
                            help_text="Subir el plan de estudios en PDF")    
    class Meta:
        icon = "doc-full"
        label = "Plan de Estudio"
        template = "courses/blocks/syllabus_block.html"

class CareerPage(Page):
    """Página para cada carrera de ingeniería"""
    
    # Información básica
    career_code = models.CharField(max_length=20, blank=True, verbose_name="Código de la carrera")
    duration = models.CharField(max_length=100, blank=True, verbose_name="Duración", 
                                help_text="Ej: 5 años")
    degree = models.CharField(max_length=200, blank=True, verbose_name="Título otorgado",
                              help_text="Ej: Ingeniero/a en Informática")
   
    
    # Imagen principal
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagen principal"
    )
    
    # Contenido principal (StreamField para máxima flexibilidad)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title", icon="title", label="Título")),
        ('paragraph', blocks.RichTextBlock(icon="pilcrow", label="Párrafo")),
        ('image', ImageChooserBlock(icon="image", label="Imagen")),
        ('list', blocks.ListBlock(blocks.CharBlock(), icon="list", label="Lista")),
    ], blank=True, use_json_field=True, verbose_name="Contenido principal")
    
    # Plan de estudios (como archivo PDF)
    syllabus_plans = StreamField(
    [('plan', SyllabusBlock())],
    blank=True,
    use_json_field=True,
    verbose_name="Planes de Estudio",
    help_text="Agrega uno o más planes de estudio con su año y PDF"
)
    # syllabus_old = models.URLField(blank=True, verbose_name="Plan de Estudios (anterior)", 
    #                                help_text="Link al PDF del plan anterior")
    # syllabus_new = models.URLField(blank=True, verbose_name="Plan de Estudios (nuevo)", 
    #                                help_text="Link al PDF del plan nuevo")
    
        # Enlaces útiles
    
    department_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Página del Departamento"
    )
    consultation_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Página de Consultas"
    )
    professional_profile_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Incumbencias Profesionales"
    )
    graduate_profile_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Perfil del Egresado"
    )
    basic_contents_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Contenidos Básicos"
    )
    # Orden de visualización
    order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    
    # RESTRICCIONES DE JERARQUÍA (agrega esto)
    parent_page_types = ['courses.CareerIndexPage']
    
    
    # Paneles de administración
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('career_code'),
            FieldPanel('duration'),
            FieldPanel('degree'),
            FieldPanel('featured_image'),
            ], heading="Información básica"),
        
        FieldPanel('body'),
        
        MultiFieldPanel([
           FieldPanel('syllabus_plans'),
        ], heading="Planes de Estudio"),
        
        MultiFieldPanel([
            FieldPanel('department_page'),
            FieldPanel('consultation_page'),
            FieldPanel('professional_profile_page'),
            FieldPanel('graduate_profile_page'),
            FieldPanel('basic_contents_page'),
        ], heading="Enlaces útiles"),
        
         MultiFieldPanel(
            [
                InlinePanel('career_subjects', label="Asignatura", panels=[
                    FieldPanel('subject'),
                    FieldPanel('year'),
                ]),
            ],heading="Asignaturas de esta carrera",
        ),
        FieldPanel('order'),        
    ]
    
    # Búsqueda
    search_fields = Page.search_fields + [
        index.SearchField('career_code'),
        index.SearchField('degree'),
    ]
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
    
    
    @property
    def has_syllabus(self):
        return bool(self.syllabus_plans)
    
    def get_context(self, request):
        context = super().get_context(request)
        # Obtenemos las asignaturas a través del modelo intermedio
        context['career_subjects'] = self.career_subjects.select_related('subject').all()
        return context

class CareerIndexPage(Page):
    """Página que lista todas las carreras"""
    
    intro = models.TextField(blank=True, verbose_name="Texto introductorio")
        # RESTRICCIONES DE JERARQUÍA
    parent_page_types = ['home.HomePage']   # Puede estar bajo HomePage
    subpage_types = ['courses.CareerPage']  # Solo puede contener carreras
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        context['careers'] = CareerPage.objects.live().order_by('order', 'title')
        return context
    
    class Meta:
        verbose_name = "Página de carreras"
        verbose_name_plural = "Páginas de carreras"

@register_snippet

# --- 1. Subject es un Snippet (ClusterableModel) ---
class Subject(ClusterableModel):
    """Asignatura como snippet reutilizable"""
    name = models.CharField(max_length=200, verbose_name="Nombre de la asignatura")
    code = models.CharField(max_length=20, blank=True, verbose_name="Código")
    workload = models.CharField(max_length=100, blank=True, verbose_name="Carga horaria")
    syllabus_doc = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Programa analítico (PDF)"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('code'),
        FieldPanel('workload'),
        FieldPanel('syllabus_doc'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        ordering = ['name']


# --- 2. Modelo intermedio para la relación Muchos a Muchos ---
class CareerSubject(models.Model):
    """Permite vincular una asignatura a una carrera, con info adicional"""
    page = ParentalKey('courses.CareerPage', on_delete=models.CASCADE, related_name='career_subjects')
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='subject_careers')
    year = models.IntegerField(blank=True, null=True, verbose_name="Año en esta carrera")

    # panels = [
    #     FieldPanel('subject'),
    #     FieldPanel('year'),
    # ]

    class Meta:
        verbose_name = "Asignatura por carrera"
        verbose_name_plural = "Asignaturas por carrera"
        # Evita duplicar la misma asignatura en una carrera
        unique_together = ('page', 'subject')


