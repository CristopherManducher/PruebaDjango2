from django import forms
from .models import Suplementos, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombreCategoria']
        widgets = {
            'nombreCategoria': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded',
                'required': True
            })
        }

class SuplementosForm(forms.ModelForm):
    class Meta:
        model = Suplementos
        fields = [
            'nombre', 'descripcion', 'precio', 'disponibilidad', 'unidadesVendidas',
            'categoria', 'oferta', 'ofertaPorcentaje', 'imagenes'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'required': True}),
            'precio': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'required': True}),
            'disponibilidad': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'required': True}),
            'unidadesVendidas': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded'}),
            'categoria': forms.Select(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'required': True}),
            'oferta': forms.CheckboxInput(attrs={'class': ''}),
            'ofertaPorcentaje': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white px-4 py-2 rounded', 'min': 0, 'max': 100}),
            'imagenes': forms.ClearableFileInput(attrs={'class': 'w-full text-gray-300'}),
        }

    def clean_imagenes(self):
        imagen = self.cleaned_data.get('imagenes')
        if imagen:
            if imagen.size > 2*1024*1024:
                raise forms.ValidationError('La imagen no puede superar los 2MB.')
            if not imagen.content_type in ['image/jpeg', 'image/png', 'image/webp']:
                raise forms.ValidationError('Solo se permiten imágenes JPEG, PNG o WEBP.')
        return imagen 