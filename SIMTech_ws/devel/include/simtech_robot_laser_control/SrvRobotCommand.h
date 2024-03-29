// Generated by gencpp from file simtech_robot_laser_control/SrvRobotCommand.msg
// DO NOT EDIT!


#ifndef SIMTECH_ROBOT_LASER_CONTROL_MESSAGE_SRVROBOTCOMMAND_H
#define SIMTECH_ROBOT_LASER_CONTROL_MESSAGE_SRVROBOTCOMMAND_H

#include <ros/service_traits.h>


#include <simtech_robot_laser_control/SrvRobotCommandRequest.h>
#include <simtech_robot_laser_control/SrvRobotCommandResponse.h>


namespace simtech_robot_laser_control
{

struct SrvRobotCommand
{

typedef SrvRobotCommandRequest Request;
typedef SrvRobotCommandResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct SrvRobotCommand
} // namespace simtech_robot_laser_control


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::simtech_robot_laser_control::SrvRobotCommand > {
  static const char* value()
  {
    return "22c7c465d64c7e74c6ae22029c7ca150";
  }

  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommand&) { return value(); }
};

template<>
struct DataType< ::simtech_robot_laser_control::SrvRobotCommand > {
  static const char* value()
  {
    return "simtech_robot_laser_control/SrvRobotCommand";
  }

  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommand&) { return value(); }
};


// service_traits::MD5Sum< ::simtech_robot_laser_control::SrvRobotCommandRequest> should match
// service_traits::MD5Sum< ::simtech_robot_laser_control::SrvRobotCommand >
template<>
struct MD5Sum< ::simtech_robot_laser_control::SrvRobotCommandRequest>
{
  static const char* value()
  {
    return MD5Sum< ::simtech_robot_laser_control::SrvRobotCommand >::value();
  }
  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommandRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::simtech_robot_laser_control::SrvRobotCommandRequest> should match
// service_traits::DataType< ::simtech_robot_laser_control::SrvRobotCommand >
template<>
struct DataType< ::simtech_robot_laser_control::SrvRobotCommandRequest>
{
  static const char* value()
  {
    return DataType< ::simtech_robot_laser_control::SrvRobotCommand >::value();
  }
  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommandRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::simtech_robot_laser_control::SrvRobotCommandResponse> should match
// service_traits::MD5Sum< ::simtech_robot_laser_control::SrvRobotCommand >
template<>
struct MD5Sum< ::simtech_robot_laser_control::SrvRobotCommandResponse>
{
  static const char* value()
  {
    return MD5Sum< ::simtech_robot_laser_control::SrvRobotCommand >::value();
  }
  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommandResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::simtech_robot_laser_control::SrvRobotCommandResponse> should match
// service_traits::DataType< ::simtech_robot_laser_control::SrvRobotCommand >
template<>
struct DataType< ::simtech_robot_laser_control::SrvRobotCommandResponse>
{
  static const char* value()
  {
    return DataType< ::simtech_robot_laser_control::SrvRobotCommand >::value();
  }
  static const char* value(const ::simtech_robot_laser_control::SrvRobotCommandResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // SIMTECH_ROBOT_LASER_CONTROL_MESSAGE_SRVROBOTCOMMAND_H
