import io
import json
import scipy.stats
import numpy as np
import math
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile, zipfile
from django.conf import settings
from wsgiref.util import FileWrapper
from scipy.stats import expon, lognorm, halfnorm, halfgennorm, ks_2samp
from scipy.interpolate import interp1d, interp2d
from scipy.interpolate import UnivariateSpline, LSQUnivariateSpline
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.shortcuts import render, render_to_response
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.urls import reverse
from django.template import loader
from .models import Station
from django.db import connection
from django.template import RequestContext
from datetime import datetime

def get_stations(request):
	stations = Station.objects.all()
	return render(request, {'stations': stations})

def get_stations_js(request):
	data = serializers.serialize("json", Station.objects.all())
	return JsonResponse({'data': data})

def open_station_histogram(request, IAGACode):
  template = loader.get_template("stationdata.html")
  context = {'load_station_histogram_image':reverse('load_station_histogram_image', args=[IAGACode])}
  return HttpResponse(template.render(context, request))

def open_coordinate_figure(request):
  selectedVal = request.GET['selectedVal']
  byGeoLat = True if request.GET['byGeoLat'] == 'true' else False 

  if (byGeoLat):
    df = pd.read_sql('select "StationName", "Latitude", "'+selectedVal+'" from "world_station_supermag" order by "Latitude"',
                    connection)
    indexNames = df[ df[selectedVal] > 0.7 ].index
    df.drop(indexNames , inplace=True)
    df.sort_values('Latitude')

    x = df["Latitude"]
  else:
    df = pd.read_sql('select "StationName", "mlatitude", "'+selectedVal+'" from "world_station_supermag" order by "mlatitude"',
                    connection)
    indexNames = df[ df[selectedVal] > 0.7 ].index
    df.drop(indexNames , inplace=True)
    df.sort_values('mlatitude')

    x = df["mlatitude"]
  
  y = df[selectedVal]
  # f2 = interp1d(x, y, kind='cubic')

  # plt.grid(True,linestyle='dashed')
  # interpolatedOutputList, lnspc = InterpolateData(df, selectedVal, 0)
  plt.xticks(np.arange(-90, 90, 10.0))
  # plt.plot(x, y, 'ro')
  # t = np.linspace(-70, 70, 7)
  # t = np.linspace(-70, 70, 5)
  t = np.linspace(-70, 70, 5)
  spl = LSQUnivariateSpline(np.array(x), np.array(y), t[1:-1])
  xs = np.linspace(-90, 90, 1000)
  plt.plot(x, y, 'ro', ms=5)
  plt.plot(xs, spl(xs), 'g-', lw=3)
  # xnew = np.linspace(-90, 90, num=115, endpoint=True)
  # for k in (1,2,3):  # line parabola cubicspline
  #   extrapolator = UnivariateSpline( x, y, k=k )
  #   y = extrapolator(xnew)
  #   label = "k=%d" % k
  #   # print(label, y)
  #   plt.plot( xnew, y, label=label)  # pylab


  fig = plt.gcf()
  # fig.set_size_inches(18.5, 10.5)
  FigureCanvasAgg(fig)
  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  plt.close(fig)
  response = HttpResponse(buf.getvalue(), content_type="image/png")
  
  response['Content-Disposition'] = 'attachment; filename="Result'+selectedVal+'.png"'
  return response

def rewrite_beta_xyz_halfgennorm(request):
    df = pd.read_sql('select "IAGACode" from "world_station"',# where world_station."BetaY" is null',
                    connection)
    XYZ = ['X', 'Y', 'Z']
    table_names = df['IAGACode'].values
    for table_name in enumerate(table_names):
        print(table_name[1])
        df = pd.read_sql('SELECT * FROM "mushrooms_station_data_'+ table_name[1] + '" order by id',
                    connection,
                    index_col='id')
        betas = [] #XYZ betta's
        for XYZvalue in XYZ:
            interpolatedOutputList, lnspc = InterpolateData(df, XYZvalue, 5)
            beta, hloc, hscale = halfgennorm.fit(lnspc)
            betas.append(beta)

        t = Station.objects.get(IAGACode= table_name[1][-3:])
        t.BetaX = betas[0]  # change field
        t.BetaY = betas[1]  # change field
        t.BetaZ = betas[2]  # change field
        t.save() 
        print(table_name[1][-3:] +' is done')

def rewrite_beta_xyz_halfgennorm_supermag(request):
    df = pd.read_sql('SELECT "IAGACode" from public.world_station_supermag where world_station_supermag."BetaY" is null;',
                    connection)
    XYZ = ['X', 'Y', 'Z', 'A', 'B', 'C']
    table_names = df['IAGACode'].values
    for table_name in enumerate(table_names):
      print(table_name[1])
      df = pd.read_sql('SELECT * FROM supermag_'+ table_name[1] + '',# order by id',
                  connection)
      betas = [] #XYZ betta's
      for XYZvalue in XYZ:
        interpolatedOutputList, lnspc = InterpolateData(df, XYZvalue, 5)
        beta, hloc, hscale = halfgennorm.fit(lnspc)
        betas.append(beta)
      
      with connection.cursor() as cursor:
        cursor.execute('UPDATE world_station_supermag SET "BetaX" = %s, "BetaY" = %s, "BetaZ" = %s, "BetaA" = %s, "BetaB" = %s, "BetaC" = %s \
                       WHERE "IAGACode" = %s', [betas[0], betas[1], betas[2], betas[3], betas[4], betas[5], table_name[1] ])
        # cursor.fetchall()
        connection.commit()
        cursor.close()
      
      print(table_name[1] +' is done')
        # cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
        # row = cursor.fetchone()
        # t = Station.objects.get(IAGACode= table_name[1][-3:])
        # t.BetaX = betas[0]  # change field
        # t.BetaY = betas[1]  # change field
        # t.BetaZ = betas[2]  # change field
        # t.save() 
        # print(table_name[1][-3:] +' is done')


def load_station_histogram_image(request, IAGACode):
    df = pd.read_sql('SELECT * FROM "mushrooms_station_data_' + IAGACode + '" order by id',
                    connection,
                    index_col='id')

    fig= plt.figure(figsize=(6,12))
    # plt.ylim([0.00000001, 2])
    # plt.xlim([0, 20])
    plt.grid(True,linestyle='dashed')
    plt.subplot(3, 1, 1)
    interpolatedOutputList, lnspc = InterpolateData(df, 'X', 5)
    binss, pdf_beta_halfgennorm, pdf_beta_expon, pdf_beta_lognorm, pdf_beta_norm = CalculateDistributions(interpolatedOutputList, lnspc)

    plt.title('X')
    plt.yscale('log')
    plt.hist(interpolatedOutputList, density=True, bins = binss)
    plt.plot(lnspc, pdf_beta_halfgennorm, color='yellow', linestyle='-',linewidth=3, label='Обобщенное нормальное')
    plt.plot(lnspc, pdf_beta_expon, color='red', linestyle='--',linewidth=1, label='Экспоненциальное')
    plt.plot(lnspc, pdf_beta_lognorm, color='green', linestyle='-',linewidth=1, label='Логнормальное')
    plt.plot(lnspc, pdf_beta_norm, color='blue', linestyle='-.',linewidth=1, label='Нормальное')
    plt.legend(loc='upper right', fontsize="small")
    
    plt.subplot(3, 1, 2)
    interpolatedOutputList, lnspc = InterpolateData(df, 'Y', 5)
    binss, pdf_beta_halfgennorm, pdf_beta_expon, pdf_beta_lognorm, pdf_beta_norm = CalculateDistributions(interpolatedOutputList, lnspc)
    
    plt.title('Y')
    plt.yscale('log')
    plt.hist(interpolatedOutputList, density=True, bins = binss)
    plt.plot(lnspc, pdf_beta_halfgennorm, color='yellow', linestyle='-',linewidth=3)
    plt.plot(lnspc, pdf_beta_expon, color='red', linestyle='--',linewidth=1)
    plt.plot(lnspc, pdf_beta_lognorm, color='green', linestyle='-',linewidth=1)
    plt.plot(lnspc, pdf_beta_norm, color='blue', linestyle='-.',linewidth=1)

    plt.subplot(3, 1, 3)
    interpolatedOutputList, lnspc = InterpolateData(df, 'Z', 5)
    binss, pdf_beta_halfgennorm, pdf_beta_expon, pdf_beta_lognorm, pdf_beta_norm = CalculateDistributions(interpolatedOutputList, lnspc)
    
    plt.title('Z')
    plt.yscale('log')
    plt.hist(interpolatedOutputList, density=True, bins = binss)
    halfgennorm = plt.plot(lnspc, pdf_beta_halfgennorm, color='yellow', linestyle='-',linewidth=3)
    expon = plt.plot(lnspc, pdf_beta_expon, color='red', linestyle='--',linewidth=1)
    lognorm = plt.plot(lnspc, pdf_beta_lognorm, color='green', linestyle='-',linewidth=1)
    norm = plt.plot(lnspc, pdf_beta_norm, color='blue', linestyle='-.',linewidth=1)
    fig = plt.gcf()
    now = datetime.now()
    # plt.savefig( settings.BASE_DIR + '/world/img/' + IAGACode + now.strftime("%m%d%Y %H%M%S") + '.png')
    FigureCanvasAgg(fig)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    
    response['Content-Disposition'] = 'attachment; filename="' + IAGACode +'.png"'
    return response

def fill_nan(A):
    '''
    interpolate to fill nan values
    '''
    inds = np.arange(A.shape[0])
    good = np.where(np.isfinite(A))
    f = scipy.interpolate.interp1d(inds[good], A[good],bounds_error=False)
    B = np.where(np.isfinite(A),A,f(inds))
    return B

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]

def InterpolateData(df, XYZ, lowestValue):
    XYZValues = df[XYZ].interpolate('linear').values
    if math.isnan(df[XYZ].values[0]):
        print('Invalid')
    interpolatedOutputList = fill_nan(XYZValues)
    medianXYZ = np.median(interpolatedOutputList)
    for i, XYZ in enumerate(interpolatedOutputList):
        newXYZ = abs(XYZ - medianXYZ)
        interpolatedOutputList[i] = newXYZ
    interpolatedOutputList = interpolatedOutputList[interpolatedOutputList > lowestValue]
    lnspc = np.linspace(interpolatedOutputList.min(), interpolatedOutputList.max(), interpolatedOutputList.size)
    return interpolatedOutputList, lnspc

def CalculateDistributions(interpolatedOutputList, lnspc):
    beta, hloc, hscale = halfgennorm.fit(lnspc)
    pdf_beta_halfgennorm = halfgennorm.pdf(lnspc, beta, hloc, hscale)
    eloc, escale = expon.fit(lnspc)
    pdf_beta_expon = expon.pdf(lnspc, eloc, escale)
    lns, lnloc, lnscale = lognorm.fit(lnspc)
    pdf_beta_lognorm = lognorm.pdf(lnspc, lns, lnloc, lnscale)
    nloc, nscale = halfnorm.fit(lnspc)
    pdf_beta_norm = halfnorm.pdf(lnspc, nloc, nscale)
    binss = int(np.trunc(np.log2(len(interpolatedOutputList)))+1)
    print(beta)
    return binss, pdf_beta_halfgennorm, pdf_beta_expon, pdf_beta_lognorm, pdf_beta_norm

# def send_zipfile(request, IAGACode):
#     """                                                                         
#     Create a ZIP file on disk and transmit it in chunks of 8KB,                 
#     without loading the whole file into memory. A similar approach can          
#     be used for large dynamic PDF files.                                        
#     """
#     temp = tempfile.TemporaryFile()
#     archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
#     # for index in range(10):
#     filename = settings.BASE_DIR +'/world/img/' + IAGACode + 'X.png' # Replace by your files here.  

#     archive.write(filename, 'X.png') # 'file%d.png' will be the
#                                                       # name of the file in the
#                                                       # zip
#     archive.close()

#     temp.seek(0)
#     wrapper = FileWrapper(temp)

#     response = HttpResponse(wrapper, content_type='application/zip')
#     response['Content-Disposition'] = 'attachment; filename=test.zip'

#     return response