

void eventSerial(){
  while(Serial.available()){
    byte inByte = Serial.read();
    
    switch(inByte){
      // TURN OFF CHANNELS
      case '1':
        changeChannelState_maintainRunningState(1,DEACTIVATE); break;
      case '2':
        changeChannelState_maintainRunningState(2,DEACTIVATE); break;
      case '3':
        changeChannelState_maintainRunningState(3,DEACTIVATE); break;
      case '4':
        changeChannelState_maintainRunningState(4,DEACTIVATE); break;
      // TURN ON CHANNELS
      case '!':
        changeChannelState_maintainRunningState(1,ACTIVATE); break;
      case '@':
        changeChannelState_maintainRunningState(2,ACTIVATE); break;
      case '#':
        changeChannelState_maintainRunningState(3,ACTIVATE); break;
      case '$':
        changeChannelState_maintainRunningState(4,ACTIVATE); break;
      
      
      case 'b':  // START STREAMING DATA
        is_running = true;
//        sampleCounter = 0;
        sampleCounter = 0x00;
        turnOnChannels();
        break;
      case 's':  // STOP STREAMING DATA
        is_running = false;
        turnOffAllChannels();  // turns off all channels
        break;
      case 'v':  // CONFIG THE MCP
        startFromScratch();
        break;
      case '?':  // PRINT MCP REGISTER VALUES
        printRegisters();
        break;
      case 'd':  // GOT TO HAVE THIS FOR OPENBCI SETUP
        Serial.println("I got your 'd'");
        break;
      case 'D':  // GOT TO HAVE THIS FOR OPENBCI SETUP
        // GUI sends D and expects to get channel settings
        Serial.print("060110");  // send fake channel settings
        sendEOT();
        break;
        
      case 't':  // RUNS A TIMED TEST AND REPORTS TO SERIAL PORT
        runTimedTest(512);  // will run until the number of samples is reached
        break;
      default:
        break;
    }// end of switch
    
  }// end of while
}



