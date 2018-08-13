## sensor_view.pyについて
```
103 def update_sensor():
110      sensor.update_sensor(isRandom=True,
111                           pyro=100,
112                           x=500, y=500, z=500,
113                          )
```

- isRandomをTrueにすることで4つの値(pyro(pyroelectric sensor:焦電センサ),  
三軸加速度センサのx, y, z軸)を乱数で生成することが可能。
- isRandomをFalseにするとpyro,x,y,zの値は、実際のセンサ値を設定することが可能。