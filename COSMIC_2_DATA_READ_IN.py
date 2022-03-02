import netCDF4 as nc
import matplotlib.pyplot as plt


f = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032\\podTc2_C2E1.2020.032.00.01.0019.G28.02_2019.3430_nc"
ds = nc.Dataset(f)
print(ds)
print(ds['TEC'])
TEC = ds['TEC'][:]
print(TEC)

print(ds['time'])
measurementTime = ds['time'][:]
print(measurementTime)

plt.plot(measurementTime, TEC)
plt.ylabel("TEC along LEO-GPS link (TECU)")
plt.xlabel("Time of GPS measurement (GPS Second)")
plt.show()