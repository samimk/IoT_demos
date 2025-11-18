'''

    Internet stvari

    Primjer korištenja MQTT za postavljanje stanja LED i očitavanje pritiska na taster na sistemu picoETF.
    Demonstrira korištenje mqtt.robust. Za svaku LED/taster se koristi zasebna tema.

    Samim Konjicija, 13.11.2023. godine

'''

from machine import Pin, PWM
import time
import network
from umqtt.robust import MQTTClient
import ujson

t1=Pin(0)
t2=Pin(1)
t3=Pin(2)
t4=Pin(3)

led0=Pin(4,Pin.OUT)
led1=Pin(5,Pin.OUT)
led2=Pin(6,Pin.OUT)
led3=Pin(7,Pin.OUT)
led4=Pin(8,Pin.OUT)
led5=Pin(9,Pin.OUT)
led6=Pin(10,Pin.OUT)
led7=Pin(11,Pin.OUT)

# RGB LED setup - PWM pinovi za kontrolu intenziteta
rgb_g = PWM(Pin(12))  # Zelena komponenta
rgb_b = PWM(Pin(13))  # Plava komponenta
rgb_r = PWM(Pin(14))  # Crvena komponenta

# Postavljanje frekvencije PWM signala na 1000 Hz
rgb_r.freq(1000)
rgb_g.freq(1000)
rgb_b.freq(1000)

# Inicijalno gašenje RGB LED
rgb_r.duty_u16(0)
rgb_g.duty_u16(0)
rgb_b.duty_u16(0)

# Uspostavljanje WiFI konekcije
nic = network.WLAN(network.STA_IF)
nic.active(True)
#nic.connect('E74KS-1','asdfghjkl')
nic.connect('SSID','PASSWORD')

while not nic.isconnected():
    print("Čekam konekciju ...")
    time.sleep(5)

print("WLAN konekcija uspostavljena")
ipaddr=nic.ifconfig()[0]

print("Mrežne postavke:")
print(nic.ifconfig())

# Funkcija za mapiranje vrijednosti 0-100 na PWM duty cycle 0-65535
def map_value(value, in_min=0, in_max=100, out_min=0, out_max=65535):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Funkcija koja se izvršava na prijem MQTT poruke
def sub(topic,msg):
    print('Tema: '+str(topic))
    print('Poruka: '+str(msg))

    # Kontrola RGB LED-a
    if topic==b'picoetf/r':
        value = int(msg)
        value = max(0, min(100, value))  # Ograničavanje na 0-100
        rgb_r.duty_u16(map_value(value))
        print('Crvena: '+str(value))
    elif topic==b'picoetf/g':
        value = int(msg)
        value = max(0, min(100, value))  # Ograničavanje na 0-100
        rgb_g.duty_u16(map_value(value))
        print('Zelena: '+str(value))
    elif topic==b'picoetf/b':
        value = int(msg)
        value = max(0, min(100, value))  # Ograničavanje na 0-100
        rgb_b.duty_u16(map_value(value))
        print('Plava: '+str(value))

    # Kontrola klasičnih LED dioda
    if topic==b'picoetf/led0':
        if msg==b'1':
            led0.on()
        else:
            led0.off()
    if topic==b'picoetf/led1':
        if msg==b'1':
            led1.on()
        else:
            led1.off()
    if topic==b'picoetf/led2':
        if msg==b'1':
            led2.on()
        else:
            led2.off()
    if topic==b'picoetf/led3':
        if msg==b'1':
            led3.on()
        else:
            led3.off()
    if topic==b'picoetf/led4':
        if msg==b'1':
            led4.on()
        else:
            led4.off()
    if topic==b'picoetf/led5':
        if msg==b'1':
            led5.on()
        else:
            led5.off()
    if topic==b'picoetf/led6':
        if msg==b'1':
            led6.on()
        else:
            led6.off()
    if topic==b'picoetf/led7':
        if msg==b'1':
            led7.on()
        else:
            led7.off()

# Funkcije za slanje MQTT poruka na pritisak tastera
def t1_publish(p):
    if t1.value():
        payload=b'1'
    else:
        payload=b'0'
    mqtt_conn.publish(b'picoetf/t1',payload)
def t2_publish(p):
    if t2.value():
        payload=b'1'
    else:
        payload=b'0'
    mqtt_conn.publish(b'picoetf/t2',payload)
def t3_publish(p):
    if t3.value():
        payload=b'1'
    else:
        payload=b'0'
    mqtt_conn.publish(b'picoetf/t3',payload)
def t4_publish(p):
    if t4.value():
        payload=b'1'
    else:
        payload=b'0'
    mqtt_conn.publish(b'picoetf/t4',payload)

# Uspostavljanje konekcije sa MQTT brokerom
mqtt_conn = MQTTClient(client_id='picoETF', server='broker.hivemq.com',user='',password='',port=1883)
mqtt_conn.set_callback(sub)
mqtt_conn.connect()
mqtt_conn.subscribe(b"picoetf/#")

print("Konekcija sa MQTT brokerom uspostavljena")

t1.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t1_publish)
t2.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t2_publish)
t3.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t3_publish)
t4.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t4_publish)

# U glavnoj petlji se čeka prijem MQTT poruke
while True:
    mqtt_conn.wait_msg()


