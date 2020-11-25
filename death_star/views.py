from django.shortcuts import redirect


def _redirect(request, url):
    nxt = request.GET.get("next", None)
    if nxt is not None:
        url += '?next=' + nxt
    return redirect(url)


def login(request):
    return _redirect(request, '/admin/login/')


def logout(request):
    return _redirect(request, '/admin/logout/')
