from __future__ import absolute_import
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import SimpleUploadedFile
from .auth import *
from .utils import *
from .models import *

logger = logging.getLogger(__name__)


@csrf_exempt
@has_perm_or_basicauth('cml.add_exchange')
@logged_in_or_basicauth()
def front_view(request):
    return Dispatcher().dispatch(request)


def error(request, error_text):
    logger.error(error_text)
    result = '{}\n{}'.format(settings.CML_RESPONSE_ERROR, error_text)
    return HttpResponse(result)


def success(request, success_test=''):
    result = '{}\n{}'.format(settings.CML_RESPONSE_SUCCESS, success_test)
    return HttpResponse(result)


def check_auth(request):
    session = request.session
    success_text = '{}\n{}'.format(settings.SESSION_COOKIE_NAME, session.session_key)
    return success(success_text)


def init(request):
    result = 'zip={}\nfile_limit={}'.format('yes' if settings.CML_USE_ZIP else 'no',
                                            settings.CML_FILE_LIMIT)
    return HttpResponse(result)


def upload_file(request):
    if request.method != 'POST':
        return error(request, 'Wrong HTTP method!')
    try:
        filename = request.GET['filename']
    except KeyError:
        return error(request, 'Need a filename param!')
    if not os.path.exists(settings.CML_UPLOAD_ROOT):
        try:
            os.makedirs(settings.CML_UPLOAD_ROOT)
        except OSError:
            return error(request, 'Can\'t create upload directory!')
    filename = os.path.basename(filename)
    temp_file = SimpleUploadedFile(filename, request.read(), content_type='text/xml')
    with open(os.path.join(settings.CML_UPLOAD_ROOT, filename), 'wb') as f:
        for chunk in temp_file.chunks():
            f.write(chunk)
    return success(request)


def import_file(request):
    try:
        filename = request.GET['filename']
    except KeyError:
        return error(request, 'Need a filename param!')
    file_path = os.path.join(settings.CML_UPLOAD_ROOT, filename)
    if not os.path.exists(file_path):
        return error(request, 'File does\'nt exists!')
    import_manager = ImportManager(file_path, )
    try:
        import_manager.import_all()
    except Exception as e:
        return error(request, str(e))
    if settings.CML_DELETE_FILES_AFTER_IMPORT:
        try:
            os.remove(file_path)
        except OSError:
            logger.error('Can\'t delete file after import: {}'.format(file_path))
    Exchange.log('import', request.user, filename)
    return success(request)


def export_query(request):
    export_manager = ExportManager()
    export_manager.export_all()
    return HttpResponse(export_manager.get_xml(), content_type='text/xml')


def export_success(request):
    export_manager = ExportManager()
    Exchange.log('export', request.user)
    export_manager.flush()
    return success(request)


class Dispatcher(object):

    def __init__(self):
        self.routes_map = {
            (u'catalog', u'checkauth'): check_auth,
            (u'catalog', u'init'): init,
            (u'catalog', u'file'): upload_file,
            (u'catalog', u'import'): import_file,
            (u'sale', u'file'): upload_file,
            (u'import', u'import'): import_file,
            (u'sale', u'checkauth'): check_auth,
            (u'sale', u'init'): init,
            (u'sale', u'query'): export_query,
            (u'sale', u'success'): export_success,
        }

    def dispatch(self, request):
        view_key = (request.GET.get('type'), request.GET.get('mode'))
        view = self.routes_map.get(view_key)
        if not view:
            raise Http404
        return view(request)
