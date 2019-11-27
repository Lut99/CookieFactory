/* ARGUMENTS.h
*    by tHE iNCREDIBLE mACHINE
*
*  Header file for Arguments.cpp.
**/

// TODO: Re-do everything using Arg this time

#ifndef ARGUMENTS_H
#define ARGUMENTS_H

#include <string>

namespace TestSuite {
    struct Arg {
        public:
            std::string key;
            void *value;
            std::size_t type;
            std::string type_name;
    };

    class Arguments {
        private:
            int size;
            int max_size;
            Arg *args;
            
            /* Does the actual storing, without any checking */
            template <typename T> void _store_pair(std::string key, T value);
            /* Stores one string / key pair */
            template <typename T> void store_pairs(std::string key, T value);
            /* Stores multiple string / key pairs */
            template <typename T, class ... Types> void store_pairs(std::string key, T value, Types... args);
        public:
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. */
            Arguments();
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. The input pattern is <std::string, T value> to assign a value to a key. */
            template <typename T> Arguments(std::string key, T value);
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. The input pattern is <std::string, T value> to assign a value to a key. */
            template <typename T, class ... Types> Arguments(std::string key, T value, Types... args);
            ~Arguments();

            /* Adds a new argument, post-initialization */
            template <typename T> void add_arg(std::string key, T value);
            
            /* Returns the value of given key */
            template <typename T> T get(std::string key);
    };
}

#endif