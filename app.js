var serialport = require('serialport');
var sleep = require('sleep');

var ser = new serialport.SerialPort('/dev/ttyUSB0', {
    baudrate: 115200,
    dataBits: 8,
    stopBits: 1,
    parity: false,
    flowControl: false
});
sleep.sleep(5);
ser.on('open', function() {
    console.log('opened serial connection');
    ser.on('data', function(data) {
        console.log('received: ' + data);
    });

ser.write([120], function(err) { console.log('err [120]: ' + err); });
sleep.sleep(5);
ser.write([131], function(err) { console.log('err [131]: ' + err); });
sleep.sleep(2);
ser.write([135], function(err) { console.log('err [135]: ' + err); });
sleep.sleep(2);
    //ser.write('\x83', function(err) { console.log('err1: ' + err); });
    //sleep.sleep(1);
    //ser.write('\x8c\x00\x05C\x10H\x18J\x08L\x10O\x20', function(err) { console.log('err2: ' + err); });
    //ser.write('\x8d\x00', function(err) { console.log('err3: ' + err); });
    //sleep.sleep(2);
    //ser.write('\x80', function(err) { console.log('err4: ' + err); });
    ser.close();
});
