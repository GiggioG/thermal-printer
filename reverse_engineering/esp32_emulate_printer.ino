#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// https://www.uuidgenerator.net/

class ServerCallbacks : public BLEServerCallbacks{
    void onConnect(BLEServer *pServer){
        Serial.println("Connected.");
    }
    void onDisconnect(BLEServer *pServer){
        pServer->startAdvertising();
        Serial.println("Disconnected, restarting advertising.");
    }
};

const int MAX_LINE = 2000;
int lineCol = 0;
void myPrint(String s){
    int len = s.length();
    if(lineCol + len >= MAX_LINE){
        Serial.println("");
        lineCol = 0;
    }
    Serial.print(s);
    lineCol += len;
}

void printReceived(BLECharacteristic *pRxCharacteristic){
    String uuid = pRxCharacteristic->getUUID().toString();
    String rxValue = pRxCharacteristic->getValue();
    // Serial.print(uuid);
    // Serial.print(" > ");
    String hexByte = "##";

    for(int i = 0; i < rxValue.length(); i++){
        uint8_t byte = rxValue[i];
        hexByte[0] = byte/16;
        hexByte[1] = byte%16;
        for(int i = 0; i < 2; i++){
            hexByte[i] += (hexByte[i] >= 10 ? ('A'-10) : '0');
        }
        myPrint(hexByte);
    }
}

BLECharacteristic *pRxChar = nullptr, *pTxChar = nullptr;

class WriteCharacteristicCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pRxCharacteristic){
        printReceived(pRxCharacteristic);
        if(pRxCharacteristic == pRxChar){
            pTxChar->setValue("\x51\x78\xA3\x01\x03\x00\x00\x0F\x24\x3F\xFF");
            pTxChar->notify();
        }
    }
};

void setup() {
    Serial.begin(115200);
    
    /// SETUP BLE
    BLEDevice::init("X6");

    BLEServer *pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    {
        BLEService *pService_AE30 = pServer->createService("AE30");

        BLECharacteristic *pChar_AE01 = pService_AE30->createCharacteristic("AE01", BLECharacteristic::PROPERTY_WRITE_NR);
        pChar_AE01->setCallbacks(new WriteCharacteristicCallbacks());
        pRxChar = pChar_AE01;

        BLECharacteristic *pChar_AE02 = pService_AE30->createCharacteristic("AE02", BLECharacteristic::PROPERTY_NOTIFY);
        pChar_AE02->addDescriptor(new BLE2902());
        pTxChar = pChar_AE02;

        BLECharacteristic *pChar_AE03 = pService_AE30->createCharacteristic("AE03", BLECharacteristic::PROPERTY_WRITE_NR);
        pChar_AE03->setCallbacks(new WriteCharacteristicCallbacks());

        BLECharacteristic *pChar_AE04 = pService_AE30->createCharacteristic("AE04", BLECharacteristic::PROPERTY_NOTIFY);
        pChar_AE04->addDescriptor(new BLE2902());

        BLECharacteristic *pChar_AE05 = pService_AE30->createCharacteristic("AE05", BLECharacteristic::PROPERTY_INDICATE);
        pChar_AE05->addDescriptor(new BLE2902());

        BLECharacteristic *pChar_AE10 = pService_AE30->createCharacteristic("AE10", BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE);
        pChar_AE10->setCallbacks(new WriteCharacteristicCallbacks());
        
        pService_AE30->start();
    }

    {
        BLEService *pService_AE3A = pServer->createService("AE3A");

        BLECharacteristic *pChar_AE3B = pService_AE3A->createCharacteristic("AE3B", BLECharacteristic::PROPERTY_WRITE_NR);
        pChar_AE3B->addDescriptor(new BLE2902());

        BLECharacteristic *pChar_AE3C = pService_AE3A->createCharacteristic("AE3C", BLECharacteristic::PROPERTY_NOTIFY);
        pChar_AE3C->addDescriptor(new BLE2902());

        pService_AE3A->start();
    }

    BLEAdvertising *pAdvertising = pServer->getAdvertising();
    pAdvertising->start();

    Serial.println("Setup done!");
}

void loop(){}