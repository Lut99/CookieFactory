/* ARGUMENTS.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  A class that can store multiple arguments by string keys. Not the faster,
*    but very variable in what it can store.
**/

#include <iostream>
#include <sstream>
#include <tuple>
#include "Arguments.h"

using namespace std;
using namespace TestSuite;

template <class ... Types> Arguments<Types...>::Arguments(Types... args) {
    // Next, store the values themselves
    this->values = tuple<Types...>(args...);
}

template <class ... Types> void Arguments<Types...>::unpack(Types &... variables) {
    // Set the variables correctly
    tie(variables...) = this->values;
}


void* test(void* arg) {
    return arg;
}

template <typename T> void* to_pointer (T input) {
    // Store it in memory
    T* mem = new T;
    (*mem) = input;
    return (void*) mem;
}
template <typename T> T from_pointer(void* input) {
    return (*((string*) input));
}


int main() {
    string name = "Carl";
    int age = 19;
    Arguments<string, int> args = Arguments<string, int>(name, age);

    string got_name;
    int got_age;
    args.unpack(got_name, got_age);

    cout << got_name << ", " << got_age << endl;
}