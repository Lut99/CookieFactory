/* ARGUMENTS.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  A class that can store multiple arguments by string keys. Not the faster,
*    but very variable in what it can store.
**/

#include <iostream>
#include <sstream>
#include "Arguments.h"

using namespace std;
using namespace TestSuite;

template <typename T>
Arg<T>::Arg(string key, T value) {
    // Create a copy of the key
    stringstream sstr;
    for (int i = 0; i < key.length(); i++) {
        sstr << key[i];
    }
    // Store both the copy and the given value
    this->key = sstr.str();
    this->value = value;
}

template <typename T>
bool Arg<T>::matches(string key) {
    return this->key.compare(key) == 0;
}
template <typename T>
T Arg<T>::get() {
    // Return the inner value
    return this->value;
}

template <class... Types> Arguments::Arguments(int size, Types... args) {

}




int main() {
    cout << "Hello there!" << endl;
}