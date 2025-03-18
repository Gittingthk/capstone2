#include <iostream>
#include <cmath>
#include <iomanip>
#include <cstdlib>
using namespace std;

double solving_Maclaurin_series(double (&function_Mac)(double), double x) {
    double sum = 0;
    double term;
    
    for(int i = 0; i <= 20; i++) {  // Use enough terms for good accuracy
        term = function_Mac(i);
        sum += term;
        if(abs(term) < 1e-10) break;  // Stop if terms become very small
    }
    
    return sum;
}

double factorial(int x) {
    if(x == 0 || x == 1)
        return 1;
        
    double result = 1;
    for(int i = 2; i <= x; i++)
        result *= i;
        
    return result;
}

double function_Mac(double x) {
    double h = 1.2;  // The value we're calculating e^h for
    return pow(h, x) / factorial(x);
}



double Truncation_Error(double solving_Mac, double x){

    return exp(x) - solving_Mac;




}


double E_a(double current_value_res, double previous_value_res){
    return current_value_res-previous_value_res;
}


int Msignificant_digits(double err){
    return (int) 2. - log10(2. *err);
}


int main()
{
    cout << left << setw(4) << "n";
    cout << left << setw(10) << "e^1.2";
    cout << left << setw(10) << "E_a";
    cout << left << setw(11) << "|eps_a|";
    cout << left << setw(1) << "m"<< endl;
    cout <<"====================================="<< endl;

    double x = 1.2, eps;  // Initialize x to 1.2
    int m, N_row_number_iteration;
    m = 2, N_row_number_iteration = 6;
    cout << setprecision(6);
    double current_value_res, previous_value_res, error, mm;
    previous_value_res = solving_Maclaurin_series(function_Mac, x);


    cout<<left<<setw(4)<<"1"<<setw(32)<<"1"<<endl;

    for(int i=1; i<N_row_number_iteration; i++)
    {
        x = i;
        current_value_res = solving_Maclaurin_series(function_Mac, x);
        eps = Truncation_Error(current_value_res,x);
        error = E_a(current_value_res,previous_value_res);
        mm = Msignificant_digits(error);
        cout<<left<<setw(4)<<i+1<<setw(10)<<current_value_res<<setw(10)<<error<<setw(14)<<eps<<mm<<endl;
        previous_value_res = current_value_res;
    

    }

return 0;

}