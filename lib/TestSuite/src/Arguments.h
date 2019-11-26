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
            int size;
            std::string *keys;
            std::tuple<Types...> values;
        public:
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. */
            Arguments(Types... values);
            ~Arguments();

            /* Sets the keys to the given values, in order as given. The given pointer isn't copied, and will be freed once the Arguments class is freed. */
            void set_keys(std::string *keys);

            /* Return the value of given key */
            void* get_elem(std::string key);
            /* Return type id of argument of given key */
            const std::type_info& get_type(std::string key);
    };

    /* Converts given void* argument to a type */
    template <typename T, class ... Types> T get_arg(Arguments<Types...> args, std::string key);
}

#endif