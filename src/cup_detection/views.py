from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from cup_detection.detector import do_detection
import glob
import os
# Create your views here.

def index(request):
	return render(request, 'cup_detection/index.html')

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        psave = os.getcwd()+'/cup_detection/static/images/pics/'
        if not os.path.exists(psave):
            os.makedirs(psave)
            
        do_detection(path_to_save_img=psave, debug=False)

        images_list = sorted(glob.glob('cup_detection/static/images/pics/*'))
        for i in range(len(images_list)) :
            images_list[i] = images_list[i][len('cup_detection/static/') : len(images_list[i])]

        output_file_url = fs.url('output.avi')
        #output_file_url = fs.url('/output.avi')

        return render(request, 'cup_detection/index.html', {
            'uploaded_file_url': uploaded_file_url,
            'output_file_url': output_file_url,
            'images_list' : images_list
        })
    return render(request, 'cup_detection/index.html')