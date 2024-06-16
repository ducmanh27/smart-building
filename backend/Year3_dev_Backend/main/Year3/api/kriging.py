import numpy as np
import pandas as pd
from math import *    
import matplotlib.pyplot as plt
import seaborn as sns


one_point_X = 3.25
one_point_Y = 1.25


class Kriging(object):
   room_x = 18
   room_y = 18
   #--------------------------------resolution---------------------------------------
   resolution = 100 
   resolutionX = 100
   resolutionY = 80
   #---------------------------------------------------------------------------------

   #----------------------------------X,Y--------------------------------------------
   default_X = np.array([0,0,6.25,8.75])           #default axis x of id 3,4,5,6
   default_Y = np.array([0.25,2.25,1.25,0.25])     #default axis y of id 3,4,5,6
   #---------------------------------------------------------------------------------

   #--------------------------------value of all known-points------------------------------
   Var = np.array([34.43, 22.03, 28.76, 24.78])    #this is default-type value of all known-points
   #---------------------------------------------------------------------------------------


   #using the spherical variogram

   nugget = 2.5
   sill = 7.5
   rang = 10

   def __init__(self, resolutionX, resolutionY, arrayVar, arrayX, arrayY, roomX, roomY):      
      self.resolutionX = resolutionX
      self.resolutionY = resolutionY
      self.default_X = np.array(arrayX)
      self.default_Y = np.array(arrayY)
      self.Var = np.array(arrayVar)
      self.room_x = roomX
      self.room_y = roomY
   def semivariance(self,h):
      nug = self.nugget 
      sill = self.sill 
      ran = self.rang
      sv = nug + sill*(3/2*h/ran-0.5*(h/ran)**3)
      if sv.shape[0] > 1:
         onescol = np.ones(sv.shape[0])         #shape[0] is number of rows, shape[1] is number of coloums
         sv = np.insert(sv, sv.shape[1], onescol, axis=1)
         onesrow = np.ones(sv.shape[1])
         sv = np.insert(sv, sv.shape[0], onesrow, axis=0)
         sv[sv.shape[0]-1][sv.shape[1]-1] = 0  # change number at the corner at the end of the matrix to 0
      else:
         onescol = np.ones(sv.shape[0])
         sv = np.insert(sv, sv.shape[1], onescol, axis=1)
         sv = sv.transpose()       
      return sv


   def distancematrix(self,X,Y):   #distance matrix of known-points
      #X is list of all x-axis points, Y is list of all coresponding x-axis points
      templist = []
      for i,j in zip(X,Y):
         for e,d in zip(X,Y):
            dist = sqrt(((i-e)**2+(j-d)**2))
            templist.append(dist)
      distancemat = np.array([templist[x:x+len(X)] for x in range(0, len(templist), len(X))])
      return distancemat


   def distancetoU(self,X1,Y1,X2,Y2):       #distance to Unknown point 
      #X1,Y1 is x axis and y axis of unknown point, X2 is list of all x-axis known-points, Y2 is corespond
      lst = []
      for k,l in zip(X2,Y2):
         dist = sqrt(((X1-k)**2)+(Y1-l)**2)
         lst.append(dist)
      uknown = np.array([lst])
      return uknown


   def OK(self, uknownX, uknownY):
      Variable = self.Var
      datax=self.default_X
      datay=self.default_Y
      #datax, datay are (x,y) of all points that we have
      #uknownX and uknownY are the (x,y) of the unknown point
      Var1 = np.reshape(Variable, (Variable.shape[0],1)) 
      Var1 = Variable.transpose()
      matdist_N = self.distancematrix(datax, datay)
      matdist_U = self.distancetoU(uknownX, uknownY, datax, datay)
      N_SV = self.semivariance(matdist_N)
      U_SV = self.semivariance(matdist_U)
      inv_N_SV = np.linalg.inv(N_SV)         
      Weights = np.matmul(inv_N_SV,U_SV)   
      Weights = np.delete(Weights, Weights.shape[0]-1, 0)   
      Estimation = np.dot(Var1, Weights) 
      return Estimation[0] 


   def interpolation(self):
      Variable = self.Var
      ResolutionX = self.resolutionX
      ResolutionY = self.resolutionY
      # X_mesh = np.linspace(np.amin(X)-1, np.amax(X) + 1, Resolution)
      # Y_mesh = np.linspace(np.amin(Y)-1, np.amax(Y) + 1, Resolution)
      X_mesh = np.linspace(0, self.room_x/2, ResolutionX)   
      Y_mesh = np.linspace(0, self.room_y/2, ResolutionY)    
      XX, YY = np.meshgrid(X_mesh, Y_mesh)   
      EX = []
      EY = []
      EZ = []
      for x in np.nditer(XX):
         EX.append(float(x))
      for y in np.nditer(YY):
         EY.append(float(y))
      Grid1 = pd.DataFrame(data={'X':EX, 'Y':EY})
      for index, rows in Grid1.iterrows():
         estimated = self.OK(rows['X'], rows['Y'])
         EZ.append(round(estimated,2))
      Grid = pd.DataFrame(data={'X':EX, 'Y':EY, 'Z':EZ})
      
      return [EX, EY, EZ]







"""
/*
 * @brief This code block is for drawing the plot, kriging using example
 */
 """
# default_X = np.array([5, 4, 11, 3, 14, 15])           #default axis x of id 3,4,5,6
# default_Y = np.array([5, 8, 11, 15, 14, 5])     #default axis y of id 3,4,5,6
# #--------------------------------value of all known-points------------------------------
# Var = np.array([32.36, 0, 0, 31.68, 30.8, 31.78])    #this is default-type value of all known-points

# resolutionX = 100
# resolutionY = 100
# k = Kriging(resolutionX, resolutionY, Var, default_X, default_Y, 18, 18)

# #------------------------------------plot points-------------------------------------------
# # cax = plt.scatter(default_X, default_Y, c=Var)
# # cbar = plt.colorbar(cax, fraction=0.1)
# # plt.title('Measured points')
# # plt.show()           #plt will not show without this
# #------------------------------------------------------------------------------------------

# #-------------------------kriging interporlation for all points in map---------------------
# """
# /*
#  * @brief test is a an array that contains 3 sub-arrays: x-asis array, y-asis array and value array.
#  *        Go to line 90 for more information.
#  */
# """
# test = k.interpolation()
# #------------------------------------------end---------------------------------------------


# x = np.array(test[0])
# y = np.array(test[1])
# z = np.array(test[2])
# print(z)
# print("_________________________________________________________")
# """
# /*
#  * @brief z is an array of "resolutionY" number elements, 
#  *        each of which is an array of "resolutionX" number elements. 
#  */
# """
# """
# /*
#  * @brief ĐÂY KHÔNG CHIA ĐƯỢC RA THEO CỘT RIÊNG HÀNG RIÊNG LÀ DO THẰNG LÌN  DƯỚI NÀY, 
#  *        trước đảo X, Y lại cho nhau nên lỗi
#  */
# """
# z = z.reshape(resolutionY, resolutionX)    
# print(len(z))


# #-----------------------------------------seaborn-----------------------------------------------
# fig, ax1 = plt.subplots(figsize=(18, 8))  #!< 18, 8 is the x and y of the room
# # sns.heatmap(z, ax=ax1, cbar=True, annot=True,  fmt=".2f", cmap= "coolwarm")  #!< có số, vẽ với màu cho nhiệt độ
# # sns.heatmap(z, ax=ax1, cbar=True, annot=True,  fmt=".2f", cmap= sns.color_palette("Greys", as_cmap=True))  #!< vẽ với màu cho dust, có số
# # sns.heatmap(z, ax=ax1, cbar=True, cmap= "coolwarm")
# sns.heatmap(z, ax=ax1, cbar=True, cmap= sns.color_palette("Greys", as_cmap=True))  #!< vẽ với màu cho dust, không có số
# ax1.invert_yaxis()
# #------------------------------------------end--------------------------------------------------


# # # res = np.array([z[x:x+20] for x in range(0, len(z), 20)])
# # # z_min, z_max = -np.abs(z).max(), np.abs(z).max()
# # c = plt.imshow(z, cmap ='Reds', vmin = np.array(test[2]).min(), vmax = np.array(test[2]).max(),
# #                extent =[x.min(), x.max(), y.min(), y.max()],
# #                   interpolation ='nearest', origin ='lower')                 
# # plt.colorbar(c)
# """
# /*
#  * @brief The two lines below is for the title of the plot and plt.show() make the plot appear.
#  */
# """
# plt.title('PM2.5 distribution at 13pm on 08/10', fontweight ="bold")
# plt.show()
"""END BLOCK"""

"""END BLOCK"""



