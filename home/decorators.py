from django.shortcuts import redirect


def business_required(redirect_url):
    
    #Views decorator that only allows restaurants to have access to this view
    
    def _wrapped(view_func, *args, **kwargs):
        def check_business(request, *args, **kwargs):
            view = view_func(request, *args, **kwargs)
            if request.user.business is False:
                return redirect(redirect_url)
            return view
        return check_business
    return _wrapped