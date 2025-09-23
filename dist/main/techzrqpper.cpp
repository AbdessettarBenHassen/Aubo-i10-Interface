
#include "inc/serviceinterface.h"
#include "inc/AuboRobotMetaType.h"
#include <cstring>   // for memset

extern "C" {

ServiceInterface* g_service = NULL;
void init_service() {
    if (!g_service)
        g_service = new ServiceInterface();
}
int robot_login(const char* host, int port, const char* user, const char* password) {
    if (!g_service) init_service();
    return g_service->robotServiceLogin(host, port, user, password);
}

int robot_startup() {
    if (!g_service) init_service();
    aubo_robot_namespace::ROBOT_SERVICE_STATE state;
    aubo_robot_namespace::ToolDynamicsParam toolDynamicsParam;
    memset(&toolDynamicsParam, 0, sizeof(toolDynamicsParam));
    return g_service->rootServiceRobotStartup(toolDynamicsParam, 6, true, true, 1000, state);
}

int robot_shutdown() {
    if (!g_service) init_service();
    return g_service->robotServiceRobotShutdown();
}

int robot_logout() {
    if (!g_service) init_service();
    return g_service->robotServiceLogout();
}


int teach_move_start(int mode, bool direction) {
    if (!g_service) init_service();
    return g_service->robotServiceTeachStart(
        static_cast<aubo_robot_namespace::teach_mode>(mode), direction
    );
}

int teach_move_stop() {
    if (!g_service) init_service();
    return g_service->robotServiceTeachStop();
}
int joint_move(double joint_angles[6], bool is_block) {
    if (!g_service) init_service();

    aubo_robot_namespace::MoveProfile_t moveProfile;
    memset(&moveProfile, 0, sizeof(moveProfile));

    return g_service->robotServiceJointMove(joint_angles, is_block);
}

// Add the four speed control functions
int set_joint_maxacc(double joint_maxacc[6]) {
    if (!g_service) init_service();
    
    aubo_robot_namespace::JointVelcAccParam jointMaxAcc;
    for (int i = 0; i < 6; i++) {
        jointMaxAcc.jointPara[i] = joint_maxacc[i];
    }
    
    return g_service->robotServiceSetGlobalMoveJointMaxAcc(jointMaxAcc);
}

int set_joint_maxvelc(double joint_maxvelc[6]) {
    if (!g_service) init_service();
    
    aubo_robot_namespace::JointVelcAccParam jointMaxVelc;
    for (int i = 0; i < 6; i++) {
        jointMaxVelc.jointPara[i] = joint_maxvelc[i];
    }
    
    return g_service->robotServiceSetGlobalMoveJointMaxVelc(jointMaxVelc);
}
	
int set_end_max_line_acc(double end_maxacc) {
    if (!g_service) init_service();
    return g_service->robotServiceSetGlobalMoveEndMaxLineAcc(end_maxacc);
}

int set_end_max_line_velc(double end_maxvelc) {
    if (!g_service) init_service();
    return g_service->robotServiceSetGlobalMoveEndMaxLineVelc(end_maxvelc);
}
// Add move control functions including continue
int robot_move_stop() {
    if (!g_service) init_service();
    return g_service->robotMoveStop();
}

int robot_move_fast_stop() {
    if (!g_service) init_service();
    return g_service->robotMoveFastStop();
}

int move_continue() {
    if (!g_service) init_service();
    return g_service->rootServiceRobotMoveControl(aubo_robot_namespace::RobotMoveContinue);
}

int move_pause() {
    if (!g_service) init_service();
    return g_service->rootServiceRobotMoveControl(aubo_robot_namespace::RobotMovePause);
}

int move_stop() {
    if (!g_service) init_service();
    return g_service->rootServiceRobotMoveControl(aubo_robot_namespace::RobotMoveStop);
}
int move_line(double joint_angles[6], bool is_block) {
    if (!g_service) init_service();
    
    // Use the second overload: robotServiceLineMove(double jointAngle[ARM_DOF], bool IsBlock)
    return g_service->robotServiceLineMove(joint_angles, is_block);
}

void cleanup_service() {
    if (g_service) {
        delete g_service;
        g_service = NULL;
    }
}

}
