#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include<unistd.h>
#include<signal.h>
#include<stdbool.h>
#include<sys/types.h>
#include<sys/wait.h>

#include "MQTTAsync.h"


#if defined(_WRS_KERNEL)
#include <OsWrapper.h>
#endif

#define ADDRESS     "192.168.0.131"
#define CLIENTID    "ExampleClientSub"
#define TOPIC       "hello"
#define PAYLOAD     "Hello World!"
#define QOS         1
#define TIMEOUT     10000L

int disc_finished = 0;
int subscribed = 0;
int finished = 0;


pid_t pid;	
bool runFlag = false;

void onConnect(void* context, MQTTAsync_successData* response);
void onConnectFailure(void* context, MQTTAsync_failureData* response);

void connlost(void *context, char *cause)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer;
	int rc;

	printf("\nConnection lost\n");
	if (cause)
		printf("     cause: %s\n", cause);

	printf("Reconnecting\n");
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		finished = 1;
	}
}



// ------------------------------------------------------------------------------------

void execArgs()
{
	// Forking a child
	char *args[]={"./edgemlops", NULL};
	pid = fork();
	// runFlag = true;

	if (pid == -1) {
		printf("\nFailed forking child..");
		return;
	} else if (pid == 0) {
		if (execvp(args[0], args) < 0) {
			printf("\nCould not execute command..");
		}
		exit(0);
	} else {
		// waiting for child to terminate
        // printf("pid = %d", pid);
        // printf("%s",parsed);
		// wait(NULL);
		return;
	}
}


// --------------------------------------------------------------------------------------------



int msgarrvd(void *context, char *topicName, int topicLen, MQTTAsync_message *message)
{
	if (pid == 0 && runFlag == true){
		printf("reached here");
		exit(0);
	}
	else if (pid > 0 || runFlag == false){
		
		// printf("Message arrived\n");
		// printf("     topic: %s\n", topicName);
		// printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
		if (!strcmp((char*)message->payload, "start")){
			// printf("Received \"hello\"! \n");
			// kill(pid,SIGSEGV);
			printf("Starting program...\n");
			execArgs();
			runFlag = true;
		}
		else if (!strcmp((char*)message->payload, "stop")){
			// printf("Received \"hello\"! \n");
			printf("Killing the program...\n");
			kill(pid,SIGSEGV);
			runFlag = false;
		}
		MQTTAsync_freeMessage(&message);
		MQTTAsync_free(topicName);
	}
    return 1;
}

void onDisconnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Disconnect failed, rc %d\n", response->code);
	disc_finished = 1;
}

void onDisconnect(void* context, MQTTAsync_successData* response)
{
	printf("Successful disconnection\n");
	disc_finished = 1;
}

void onSubscribe(void* context, MQTTAsync_successData* response)
{
	printf("Subscribe succeeded\n");
	subscribed = 1;
}

void onSubscribeFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Subscribe failed, rc %d\n", response->code);
	finished = 1;
}


void onConnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Connect failed, rc %d\n", response->code);
	finished = 1;
}


void onConnect(void* context, MQTTAsync_successData* response)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_responseOptions opts = MQTTAsync_responseOptions_initializer;
	int rc;

	printf("Successful connection\n");

	printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n"
           "Press Q<Enter> to quit\n\n", TOPIC, CLIENTID, QOS);
	opts.onSuccess = onSubscribe;
	opts.onFailure = onSubscribeFailure;
	opts.context = client;
	if ((rc = MQTTAsync_subscribe(client, TOPIC, QOS, &opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start subscribe, return code %d\n", rc);
		finished = 1;
	}
}




int main(int argc, char* argv[])
{

	// execArgs();
	// if (pid > 0)
	MQTTAsync client;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer;
	MQTTAsync_disconnectOptions disc_opts = MQTTAsync_disconnectOptions_initializer;
	int rc;
	int ch;
	

	if ((rc = MQTTAsync_create(&client, ADDRESS, CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL))
			!= MQTTASYNC_SUCCESS)
	{
		printf("Failed to create client, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto exit;
	}

	if ((rc = MQTTAsync_setCallbacks(client, client, connlost, msgarrvd, NULL)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to set callbacks, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}

	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}
	
	while (!subscribed && !finished)
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif

	if (finished)
		goto exit;

	do 
	{
		ch = getchar();
	} while (ch!='Q' && ch != 'q');

	disc_opts.onSuccess = onDisconnect;
	disc_opts.onFailure = onDisconnectFailure;
	if ((rc = MQTTAsync_disconnect(client, &disc_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start disconnect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}
 	while (!disc_finished)
 	{
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif
 	}

destroy_exit:
	printf("Force exited \n");
	MQTTAsync_destroy(&client);
exit:
 	return rc;
}
