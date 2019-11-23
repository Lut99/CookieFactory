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
            int size;
            std::string *keys;
            std::tuple<Types> values;
        public:
            /* The Arguments class stores many different types of variables, stored in a list and accessible by a key. */
            Arguments(Types... values);
            ~Arguments();

            /* Sets the keys to the given values, in order as given. The given pointer isn't copied, and will be freed once the Arguments class is freed. */
            void set_keys(std::string *keys);

            /* Returns value for given key. */
            template<class T> T &operator[] (std::string key);
    };
}

#endif