from django.shortcuts import render, redirect
from .models import LojaConfiguracao
from .forms import LojaConfiguracaoForm

def configurar_loja(request):
    configuracao, created = LojaConfiguracao.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = LojaConfiguracaoForm(request.POST, instance=configuracao)
        if form.is_valid():
            form.save()
            return redirect('configurar_loja')
    else:
        form = LojaConfiguracaoForm(instance=configuracao)
    return render(request, 'loja/configurar_loja.html', {'form': form})

