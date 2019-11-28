/* ARGUMENTS.h
*    by tHE iNCREDIBLE mACHINE
*
*  Header file for Arguments.cpp.
**/

#ifndef ARGUMENTS_H
#define ARGUMENTS_H

#include <string>

namespace TestSuite {
    template <class ... Types> class Arguments {
        private:
            std::tuple<Types...> values;
        public:
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. Input the values here, give the keys using set_keys(). */
            Arguments(Types... args);
            
            /* Returns the arguments in-order */
            void unpack(Types &... variables);
    };
}

#endif