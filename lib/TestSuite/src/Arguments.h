/* ARGUMENTS.h
*    by tHE iNCREDIBLE mACHINE
*
*  Header file for Arguments.cpp.
**/

#ifndef ARGUMENTS_H
#define ARGUMENTS_H

#include <string>

namespace TestSuite {
    template <class T> class Arg {
        private:
            std::string key;
            T value;
        public:
            /* The arg class contains the key & value for a single argument of given type T. */
            Arg(std::string key, T value);

            /* Checks if this argument equals given key. */
            bool matches(std::string key);
            /* Returns the value of this argument. */
            T get();
    };

    template <class ... Types> class Arguments {
        private:
            void* args;

            /* Basecase for recursively adding each element to the internal elements list. */
            template <class T> void add_element(T arg);
            /* Recurse case for recursively adding each element to the internal elements list. */
            template <class T, class ... Rest> void add_element(T arg, Rest ... rest);
        public:
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. */
            Arguments(int size, Types ... args);
    };
}

#endif