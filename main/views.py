from django.shortcuts import render
import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
import matplotlib as plt1
import matplotlib
matplotlib.use('Agg')
import geojsoncontour
from scipy.ndimage.filters import gaussian_filter
from sklearn import preprocessing





# Create your views here.
#методы выполняемые при переходе на определенную страницу


def index(request):  #метод выполняемый при переходе на главную страницу (index)
    date = 0
    time = 0
    parametr = None
    geojson = None

    if request.method == 'POST':        #передачи параметров из формы введенных пользователем на главной странице
        date = request.POST['date']
        time = request.POST['time'] + ':00.000'
        parametr = request.POST['parametr']

    path = ''
    if date == '2015-03-17':
        path = r'C:\Users\Марсик\Desktop\файлы\2015-03-17'
    if date == '2015-06-23':
        path = r'C:\Users\Марсик\Desktop\файлы\2015-06-23'
    if date == '2015-09-11':
        path = r'C:\Users\Марсик\Desktop\файлы\2015-09-11'
    if date == '2015-10-07':
        path = r'C:\Users\Марсик\Desktop\файлы\2015-10-07'
    if date == '2015-12-20':
        path = r'C:\Users\Марсик\Desktop\файлы\2015-12-20'
    if path != '':
      allfiles = glob.glob(os.path.join(path, "*.min"))# считывание всех файлов формата min из папки по пути path
      frame = pd.DataFrame(columns=['IAGA COD','Station Name', 'Latitude', 'Longitude','DATE', 'TIME',  'X', 'Y', 'Z', 'F']) #преобразование исходного формата данных в DataFrame
      colnames = ['DATE', 'TIME', 'DAY', 'X', 'Y', 'Z', 'F', '|']
      for nevFiles in allfiles: #запись всех файлов в один дата фрейм и их преобразование
        temp = pd.read_csv(nevFiles, comment='#', sep= '\s+', skiprows=lambda x: x in [0, 1], names=colnames, header= None)
        lat = temp.at[2, 'DAY']
        lon = temp.at[3, 'DAY']
        stname = temp.at[0, 'DAY']
        iaga = temp.at[1, 'DAY']
        temp = pd.read_csv(nevFiles, sep='\s+', skiprows=25, names=colnames, header=None)
        temp.insert(loc=0, column="IAGA COD", value=iaga)
        temp.insert(loc=1, column="Station Name", value=stname)
        temp.insert(loc=2, column="Latitude", value=lat)
        temp.insert(loc=3, column="Longitude", value=lon)
        del temp['|'], temp['DAY']
        frame = pd.concat([frame, temp], ignore_index=True)

      frame = frame.astype({"Latitude": float, "Longitude": float})
      filt = frame.loc[(frame['TIME'] == time)] #фильрация данных по времени введенное пользователем

      points = filt[['Latitude', 'Longitude' , parametr]].to_numpy() #запись их в массив

      y = points[:, 0] #долгота
      x = points[:, 1] #широта
      z = points[:, 2] #геомагнитные значения зафиксированные в этих точках в определнное время


      normalize = preprocessing.normalize([z]) #нормализация данных магнитного параметра
      z = normalize[0]

      numcols, numrows = 360, 180 #узлы регулярной сетки

      xi = np.linspace(np.min(x), np.max(x), numcols) #узлы регулярной сетки
      yi = np.linspace(np.min(y), np.max(y), numrows) #узлы регулярной сетки


      triang = plt1.tri.Triangulation(list(x), list(y)) #триангуляция делоне точек на карте
      interpolator = plt1.tri.LinearTriInterpolator(triang, list(z)) #интерполяция гмп значений и точек станций
      Xi, Yi = np.meshgrid(xi, yi) #построение регулярной сетки

      zi = interpolator(Xi, Yi) #пространственная интерполяция на регулярную сетку
      zi = gaussian_filter(zi, sigma=.9) #фильтр сглаживания

      #levels = len(np.unique(z))  # len(np.unique(z))

      contour = plt.contour(Xi, Yi, zi, levels=20, cmap=plt.cm.jet, extend='both', antialiased=True) #построение контура изолиний
      geojson = geojsoncontour.contour_to_geojson(  #формирование формата GeoJson
        contour=contour,
        stroke_width=10
       )

    return render(request, "main/index.html", context={'geojson': geojson}) #передача geojson в шаблон index

def about(request): #метод выполняемый при переходе на  страницу "О проекте"(about)
    return render(request, 'main/about.html')



