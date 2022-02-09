//Изработиле
//Иван Марковски 185051
//Кристијан Николиќ 185006
#include <SoftwareSerial.h>
#include "DFRobotDFPlayerMini.h"
#include "Arduino.h"
//Библиотеки потреби за мемориска и bluetooth

//3 променливи за контролни пинови на мултиплексер CD4051
int a=6;
int b=5;
int c=4;


// серијал за MP3-TF 16P 
SoftwareSerial mySoftwareSerial(10, 11); // RX, TX

// објект од класата за MP3-TF 16P
DFRobotDFPlayerMini myDFPlayer;

// серијал за bluetooth модулата HC-06
SoftwareSerial hc06(2,3);

int bluetoothFlag = 0; // знаменце за bluetooth аудио(0) и за аудио од мемориска(1)
int sdPlaying = 0;  // знаменце дали е пуштено музика од мемориска
// стринг за упатство и error
String manual = "--------||--------\nФормат за упатство:\nиме_команда додатни аргументи\n--------||--------\nКоманди:\nmanual - За упатство (работи со m,man,help,h) \nplay песна(p) - За да се пушти песна\npause - За пауизирање на песна\nresume - За продолжување песна(r)\nstop - за прекинување на песна\nnext - за пуштање на следна песна\nsd/bt - за промена\n--------||--------";
String errorNext = "Нема песна во низа!";

char python; // променлива за карактер кој е пратен од python код

void setup(){
// Иницијализација за серијал монитор
Serial.begin(9600);

//Иницијализација на мемориската сериски порт
mySoftwareSerial.begin(9600);

//Иницијализација на bluetooth сериски порт
hc06.begin(9600);

// иницијализирање на пиновите од 4-6 за излез за мултиплексерот
pinMode(a,OUTPUT);
pinMode(b,OUTPUT);
pinMode(c,OUTPUT);
        digitalWrite(a,LOW);
        digitalWrite(b,LOW);
        digitalWrite(c,LOW);

//иницијализирање на мемориската
myDFPlayer.begin(mySoftwareSerial);


}
void loop(){

        //почетна вредност за променливата, доколку нема пристигнато ништо од страна на python кодот
        python = 'a';
        //Запишување на серијал монитор од телефон односно од HC-06
        if (hc06.available()){
        Serial.write(hc06.read());
        }
        
        //Читање од серијал монитор
        if (Serial.available()){
        python = Serial.read();
        }

        // Свич за променливата python
        switch(python){
        case '0':
          //прочитај го упатството за мемориската и за bluetooth
          hc06.print(manual);
          break;
        case '1':
        if(bluetoothFlag){ // ако е пристигнато 1 од python и е вклучена мемориската пушти ја песната, ако е вклучен bluetooth печати error
          myDFPlayer.play(1);
          sdPlaying = 1;
        }
        else{
          hc06.print(errorNext);
        }
          break;  
        case '2': // стоп на песната на мемориска
          if(bluetoothFlag){
          myDFPlayer.stop();
          sdPlaying = 0;
          }
          break;
        case '3': // следната песна на мемориска
          if(bluetoothFlag){
          myDFPlayer.next();
          }
          break;
        case '4': // враќање назад на мемориска
          if(bluetoothFlag){
          myDFPlayer.previous();
          }
          break;
        case '5': // продолжува песна на мемориска доколку е паузирана
        if(bluetoothFlag){
        if(sdPlaying==0)
          {
          myDFPlayer.start();
          }
        else{ // доколку не е паузирана, се паузира песната
          myDFPlayer.pause();
          sdPlaying = 0;
        }
        }
          break;
        case 's': // проверка дали се вклучува читање од мемориска
          hc06.print("Вклучена е мемориската! Напиши play за да започне музика");
          bluetoothFlag = 1;
          break;
        case 'b'://проверка дали се вклучува читање од bluetooth
          hc06.print("Вклучен е bluetooth!");
          hc06.print(manual);
          myDFPlayer.stop();
          bluetoothFlag = 0;
          break;
        }
        
        if (bluetoothFlag == 0){ // Сетирање на мултиплексерот за да слуша аудио од bluetooth
        digitalWrite(a,LOW); //0
        digitalWrite(b,LOW); //0
        digitalWrite(c,LOW); //0
        }
        else if(bluetoothFlag == 1) // Сетирање на мултиплексерот за да слуша аудио од мемориска
        {
        digitalWrite(a,HIGH); //1
        digitalWrite(b,LOW); //0
        digitalWrite(c,LOW); //0
        }// а е најмалиот бит, b е вториот најмал, c е најголемиот бит
        
}
