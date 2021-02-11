

# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos, machine
print('uos and machine is import')
# uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
print('gc is import')
#import webrepl
#webrepl.start()
gc.collect()
print('gc.collect() is run')

#############################################################################
# Networck settings
import network, ujson, time # Привязали модуль network
from json_generator import JSON_gen

########################## Заводские настройки ##############################
def DefaultSettings():
    SSID = 'ESP-Relay'
    AUTH = network.AUTH_WPA_WPA2_PSK
    CH = 11
    HIDEN = False
    PASS = 'ESPRelay'
    HOSTNAME = 'ESP-Relay by Abrakadabra Workshop'

    ap_if = network.WLAN(network.AP_IF)     # Создаем экземпляр интервейса точки доступа
    ap_if.active(True)                      # Запускаем интерфейс
    ap_if.config(essid = SSID,              # Конфигурация
                 channel = CH,
                 hidden = HIDEN,
                 authmode = AUTH,
                 password = PASS)
    networtSettings = ap_if.ifconfig()      # Забираем данные о настройках сети и выводим в консоль (REPL on UART(0))

    print('Module is started on default settings:')
    print('Mode = Access Point (AP)')
    print('SSID = ' + SSID)
    print('Channel = ', CH)
    print('Hidden = ', HIDEN)
    print('Authmode = ' , AUTH, ' - AUTH_WPA_WPA2_PSK')
    print('Password = ' + PASS)
    print('Host name = ' + HOSTNAME)
    print('IP adress = ' + networtSettings[0])
    print('Subnet mask = ' + networtSettings[1])
    print('Gateway = ' + networtSettings[2])
    print('DNS adress = ' + networtSettings[3])

    #Создаем словарь со всеми базовыми переменными
    dictConf = {'defSettings' : False,
                'mode' : 'AP',                      # Access Point
                'ap_ssid' : SSID,                      # SSID
                'channel' : CH,                     # Chennal
                'hidden' : HIDEN,                   #
                'authmode' : AUTH,                  # authmode
                'ap_passwd' : PASS,                    # Password
                'hostname' : HOSTNAME,              # DHCP host name
                'ip' : networtSettings[0],          # ip adress
                'subnet' : networtSettings[1],      # subnet mask
                'gateway' : networtSettings[2],     # gateway
                'dns' : networtSettings[3],         # dns adress
                'sta_DHCP' : True,
                'sta_ssid' : 'ssid',                  # SSID
                'sta_passwd' : 'pass'}                # Password

    #... и помещаем его в конфиг файл
    config = JSON_gen(file = 'config.json')      # Создаем экземпляр конфигурации
    config.write_to_JSON(dictConf)               # Выполняем запись

########################## Настройки из конфига #############################
def ConfigSettings(configDict):
    print('Module is started on Config settings:')

    dictAuthmode = {0 : '0 - AUTH_OPEN',
                    1 : '1 - AUTH_WEP',
                    2 : '2 - AUTH_WPA_PSK',
                    3 : '3 - AUTH_WPA2_PSK',
                    4 : '4 - AUTH_WPA_WPA2_PSK'}

    dictStatus = {0 : 'Status 0 - STAT_IDLE ',                 # нет соединения и активности.
                  1 : 'Status 1 - STAT_CONNECTING ',           # соединение в процессе.
                  2 : 'Status 2 - STAT_WRONG_PASSWORD ',       # соединение установить не удалось из-за неправильного пароля.
                  3 : 'Status 3 - STAT_NO_AP_FOUND ',          # соединение установить не удалось, потому что ни одна точка доступа не ответила.
                  4 : 'Status 4 - STAT_CONNECT_FAIL ',         # соединение установить не удалось из-за других проблем.
                  5 : 'Status 5 - STAT_GOT_IP '}               # соединение установлено успешно.

    if configDict['mode'] == 'AP':
        ap_if = network.WLAN(network.AP_IF)                    # Создаем экземпляр интервейса точки доступа
        ap_if.active(True)                                     # Запускаем интерфейс
        ap_if.config(essid = configDict['ap_ssid'],            # Конфигурируем данными из конфига
                     channel = configDict['channel'],
                     hidden = configDict['hidden'],
                     authmode = configDict['authmode'],
                     password = configDict['ap_passwd'])

        networtSettings = ap_if.ifconfig()                     # Забираем данные о настройках сети и выводим в консоль (REPL on UART(0))

        print('Mode = Access Point (AP)')
        print('SSID = ' + configDict['ap_ssid'])
        print('Channel = ', configDict['channel'])
        print('Hidden = ', configDict['hidden'])
        print('authmode = ' , dictAuthmode[configDict['authmode']])
        print('Password = ' + configDict['ap_passwd'])
        print('IP adress = ' + networtSettings[0])
        print('Subnet mask = ' + networtSettings[1])
        print('Gateway = ' + networtSettings[2])
        print('DNS adress = ' + networtSettings[3])

    elif configDict['mode'] == 'STA':
        sta_if = network.WLAN(network.STA_IF)               # Создаем экземпляр интервейса станции
        sta_if.active(True)                                 # Запускаем интерфейс

        if configDict['sta_DHCP'] == False:                 # Если у нас статический ip  тогда до подключения задаем его
            sta.ifconfig((configDict['ip'], configDict['subnet'], configDict['gateway'], configDict['dns'],))

        sta_if.connect(configDict['sta_ssid'], configDict['sta_passwd'])                # Пытаемся подключиться
        attempt  = 1
        print('Attempt #1')
        while sta_if.status() != network.STAT_GOT_IP:  # пока подключение не появилось крутимся в цикле
            if sta_if.status() != network.STAT_CONNECTING:
                attempt  += 1
                if attempt  > 5 or sta_if.status() == network.STAT_WRONG_PASSWORD or sta_if.status() == network.STAT_IDLE:
                    print('Connection error')
                    print(dictStatus.get(sta_if.status()))     # Пишем статус
                    DefaultSettings()
                    break

                print(dictStatus.get(sta_if.status()))     # Пишем статус
                print('Attempt #', attempt)
                sta_if.connect(configDict['sta_ssid'], configDict['sta_passwd'])                # Пытаемся подключиться

            print(dictStatus.get(sta_if.status()))     # Пишем статус
            time.sleep(1)                              # один раз в секунду

        if sta_if.isconnected():
            print(dictStatus.get(sta_if.status()))     # Пишем статус
            if configDict['sta_DHCP'] == True:
                networtSettings = ap_if.ifconfig()
                print('Mode = Station DHCP (STA_DHCP_ON)')
                print('Access point SSID = ' + configDict['sta_ssid'])
                print('IP adress = ' + networtSettings[0])
                print('Subnet mask = ' + networtSettings[1])
                print('Gateway = ' + networtSettings[2])
                print('DNS adress = ' + networtSettings[3])
            else:
                print('Mode = Station static (STA_DHCP_OFF)')
                print('Access point SSID = ' + configDict['sta_ssid'])
                print('IP adress = ' + configDict['ip'])
                print('Subnet mask = ' + configDict['subnet'])
                print('Gateway = ' + configDict['gateway'])
                print('DNS adress = ' + configDict['dns'])
    else:
        print('Mode error!')
        DefaultSettings()

#############################################################################
def checkingKeys(dictCheck):
    # Эталонное множество (перечень ключей)
    keysBase = {'defSettings', 'mode', 'ap_ssid','channel', 'hidden',
                'authmode', 'ap_passwd', 'hostname', 'ip', 'subnet',
                'gateway', 'dns','sta_DHCP', 'sta_ssid', 'sta_passwd'}
    # Проверяемое множество (перечень ключей) делаем из словаря
    keysCheck = set(dictCheck.keys())

    #intersect_keys = keysBase.intersection(keysCheck) # возвращает совпадения
    #print('intersect_keys')
    #print(intersect_keys)

    added = keysBase - keysCheck    # Возвращает те лючи которые есть в keysBase и отсутствуют в keysCheck
    #print('added')
    #print(added)

    #removed = keysCheck - keysBase # Возвращает те лючи которые есть в keysCheck и отсутствуют в keysBase
    #print('removed')
    #print(removed)
    return added    #если все клчи есть то вернёт set()
#############################################################################

#Существует ли конфиг?
try:
    #Если существует конфиг файл
    configFile = open('config.json') # Пробуем открыть конфиг файл...
    config = ujson.loads(configFile.read())
    configFile.close() # Закрываем файл.

    print('Configuration file was found!')

     #...то проверяем все ли ключи на месте
    if checkingKeys(config) == set(): #если все ключи на месте
        #Если нужно загрузиться с заводскими настройками
        if config.get('defSettings') == True:   # Если defSettings True
            DefaultSettings()                   # Запускаемся с заводскими настройками
        else:                                   # Если defSettings False
            ConfigSettings(config)                    # Запускаемся с настройками из конфига
    else:
        print('The following keys are not in the configuration file:')
        print(checkingKeys(config))
        DefaultSettings()                   # Запускаемся с заводскими настройками

except OSError:# или если конфига нет!
    # Загрузка с заводскими настройками
    print('Config file not found!')
    # Default settings
    DefaultSettings()


