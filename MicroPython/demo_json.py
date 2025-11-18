'''

    Internet stvari

    Primjer korištenja MQTT za postavljanje stanja LED i očitavanje pritiska na taster na sistemu picoETF.
    Demonstrira korištenje mqtt.robust i ujson. Koriste se zbirne teme za sve LED odnosno za sve tastere. Pojedinačne
    LED/tasteri se identificiraju korištenjem JSON-formatiranih poruka.

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

ledice=[led0,led1,led2,led3,led4,led5,led6,led7]

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
nic.connect('SSID', 'PASSWORD')

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
    parsed=ujson.loads(msg)
    print('Tema: '+str(topic))
    print('Poruka: '+str(msg))

    # Provjera da li je poruka za RGB LED kontrolu
    if "R" in parsed and "G" in parsed and "B" in parsed:
        r_val = parsed["R"]
        g_val = parsed["G"]
        b_val = parsed["B"]
        print('RGB LED kontrola - R: '+str(r_val)+', G: '+str(g_val)+', B: '+str(b_val))

        # Ograničavanje vrijednosti na raspon 0-100
        r_val = max(0, min(100, r_val))
        g_val = max(0, min(100, g_val))
        b_val = max(0, min(100, b_val))

        # Postavljanje PWM duty cycle-a za svaku komponentu
        rgb_r.duty_u16(map_value(r_val))
        rgb_g.duty_u16(map_value(g_val))
        rgb_b.duty_u16(map_value(b_val))

    # Kontrola klasičnih LED dioda
    elif "led" in parsed and "stanje" in parsed:
        led=parsed["led"]
        stanje=parsed["stanje"]
        print('LED: '+str(led))
        print('Stanje: '+str(stanje))

        if stanje==1:
            ledice[led].on()
        else:
            ledice[led].off()

# Funkcije za slanje MQTT poruka na pritisak tastera
def t1_publish(p):
    if t1.value():
        msg=b'{ "taster": 1,"stanje": 1 }'
    else:
        msg=b'{ "taster": 1,"stanje": 0 }'
    mqtt_conn.publish(b'picoetf/tasteri',msg)
def t2_publish(p):
    if t2.value():
        msg=b'{ "taster": 2,"stanje": 1 }'
    else:
        msg=b'{ "taster": 2,"stanje": 0 }'
    mqtt_conn.publish(b'picoetf/tasteri',msg)
def t3_publish(p):
    if t3.value():
        msg=b'{ "taster": 3,"stanje": 1 }'
    else:
        msg=b'{ "taster": 3,"stanje": 0 }'
    mqtt_conn.publish(b'picoetf/tasteri',msg)
def t4_publish(p):
    if t4.value():
        msg=b'{ "taster": 4,"stanje": 1 }'
    else:
        msg=b'{ "taster": 4,"stanje": 0 }'
    mqtt_conn.publish(b'picoetf/tasteri',msg)

# Uspostavljanje konekcije sa MQTT brokerom
mqtt_conn = MQTTClient(client_id='picoETF', server='broker.hivemq.com',user='',password='',port=1883)
mqtt_conn.set_callback(sub)
mqtt_conn.connect()
mqtt_conn.subscribe(b"picoetf/ledice")

print("Konekcija sa MQTT brokerom uspostavljena")

t1.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t1_publish)
t2.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t2_publish)
t3.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t3_publish)
t4.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=t4_publish)

# U glavnoj petlji se čeka prijem MQTT poruke
while True:
    mqtt_conn.wait_msg()




