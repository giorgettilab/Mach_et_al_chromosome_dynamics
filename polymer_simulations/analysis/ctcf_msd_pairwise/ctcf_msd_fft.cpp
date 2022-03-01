#include <iostream>
#include <fstream>
#include <mpi.h>
#include <string>
#include <cstring>
#include <cmath>
#include <fftw3.h>

void ACF(fftw_complex *in_local, fftw_complex *out_local, fftw_complex *out2_local, int numframes)
{
    fftw_plan p, q;
    p = fftw_plan_dft_1d(numframes, in_local, out_local, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p);
    for (int j = 0; j < numframes; j++)
    {
        out_local[j][0] =
            out_local[j][0] * out_local[j][0] +
            out_local[j][1] * out_local[j][1];
        out_local[j][1] = 0;
    }

    q = fftw_plan_dft_1d(numframes, out_local, out2_local, FFTW_BACKWARD, FFTW_ESTIMATE);
    fftw_execute(q);
    for (int j = 0; j < numframes; j++)
    {
        out2_local[j][0] /= numframes;
        out2_local[j][1] /= numframes;
        out2_local[j][0] = out2_local[j][0] / double(numframes / 2 - j);
    }
    fftw_destroy_plan(p);
    fftw_destroy_plan(q);
    fftw_cleanup();
}

void msd_aver_single_fft_1d(double *arr, double *msd, int numframes)
{
    double *D, *S1, *S2;
    double Q, temp_val;
    fftw_complex *in_local_x, *out_local_x, *out2_local_x;
    D = new double[numframes + 1];
    S1 = new double[numframes];
    S2 = new double[numframes];
    in_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out2_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);

    Q = 0.0;
    for (int j = 0; j < numframes; j++)
    {
        in_local_x[j][0] = arr[j];
        in_local_x[j][1] = 0;
        out_local_x[j][0] = 0;
        out_local_x[j][1] = 0;
        out2_local_x[j][0] = 0;
        out2_local_x[j][1] = 0;
    }
    for (int j = numframes; j < 2 * numframes; j++)
    {
        in_local_x[j][0] = 0;
        in_local_x[j][1] = 0;
        out_local_x[j][0] = 0;
        out_local_x[j][1] = 0;
        out2_local_x[j][0] = 0;
        out2_local_x[j][1] = 0;
    }
    ACF(in_local_x, out_local_x, out2_local_x, 2 * numframes);
    for (int j = 0; j < numframes; j++)
    {
        S2[j] = out2_local_x[j][0]; // S2 is calculated
        temp_val =
            in_local_x[j][0] * in_local_x[j][0]; // D[j] is calculated
        D[j] = temp_val;
        Q += temp_val;
    }
    Q *= 2;
    D[numframes] = 0;
    for (int j = 0; j < numframes; j++)
    {
        Q = Q - D[j - 1] - D[numframes - j];
        S1[j] = Q / double(numframes - j);
    }
    for (int j = 0; j < numframes; j++)
    {
        msd[j] += S1[j] - 2 * S2[j];
    }
}

void msd_1d(double *arr, double *msd, int numberFrames)
{
    int *count = new int[numberFrames];
    for (int i = 0; i < numberFrames; i++)
    {
        for (int j = i + 1; j < numberFrames; j++)
        {
            msd[j - i] += (arr[i] - arr[j]) * (arr[i] - arr[j]);
            count[j - i] += 1;
        }
    }
    for (int i = 1; i < numberFrames; i++)
    {
        if (count[i] != 0)
            msd[i] /= count[i];
        else
            msd[i] = 0;
    }
    delete[] count;
    count = NULL;
}

int main(int argc, char *argv[])
{

    int rank, commsize, ierr;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &commsize);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    int numberBeads, numberFrames, skip_rows;
    int num_useless_arguments = 1;
    std::string emp, line;
    std::string mypath;
    std::fstream in;
    double *ctcf_dst, *ctcf_msd, *joint_msd;
    skip_rows = 0;

    if (rank == 0)
    {
        std::cout << "Your input:\n";
        for (unsigned int i = 0; i < argc; i++)
            std::cout << argv[i] << ' ';
        std::cout << std::endl;
        if (argc < 2)
        {
            ierr = 1;
            std::cerr << "Number of arguments is zero, please check help and/or your input." << std::endl;
            MPI_Finalize();
            return 1;
        }
    }

    for (unsigned int i = 0; i < argc; i++)
    {
        if (rank == 0 && (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0))
        {
            std::cout << "Program to calculate pairwise MSD using dsts file.\n"
                      << "Output MSD file will be in the same folder with suffix \'_msd_ctcf.dat\'."
                      << "\nInputs:\n"
                      << "-s, --skip     starting line, consider resolution by yourself\n"
                      << "-n, --number   number of useless arguments, default: 1\n"
                      << "-p, --path     defines a path to a file to be analyzed\n"
                      << std::endl;
            ierr = 3;
            MPI_Finalize();
            return 3;
        }
        if (strcmp(argv[i], "-p") == 0 || strcmp(argv[i], "--path") == 0)
        {
            mypath = argv[i + 1];
        }
        if (strcmp(argv[i], "-s") == 0 || strcmp(argv[i], "--skip") == 0)
        {
            skip_rows = atoi(argv[i + 1]);
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);
    if (rank == 0)
    {
        in.open(mypath, std::ios::in);
        if (!in.is_open())
        {
            std::cerr << "Somthing went wrong with opening dsts file" << std::endl;
            MPI_Finalize();
            return 15;
        }
        numberFrames = -1; // because of the header line
        while (getline(in, line))
        {
            ++numberFrames;
        }
        in.close();
        numberFrames -= skip_rows;
    }
    MPI_Bcast(&numberFrames, 1, MPI_INT, 0, MPI_COMM_WORLD);
    ctcf_dst = new double[numberFrames];
    ctcf_msd = new double[numberFrames];
    for (int i = 0; i < numberFrames; i++)
    {
        ctcf_dst[i] = 0;
        ctcf_msd[i] = 0;
    }
    if (rank == 0)
        std::cout << "1st reading is over by " << rank << std::endl;
    in.open(mypath, std::ios::in);
    getline(in, emp);
    int line_number = 0;
    while (line_number < skip_rows)
    {
        getline(in, line);
        ++line_number;
    }
    line_number = 0;
    while (getline(in, emp))
    {
        line_number++;
        in >> ctcf_dst[line_number];
        for (unsigned int i = 1; i < num_useless_arguments; i++)
        {
            in >> emp;
        }
    }
    in.close();
    if (rank == 0)
        std::cout << "2nd reading is over by " << rank << '\t' << numberFrames << std::endl;

    msd_aver_single_fft_1d(ctcf_dst, ctcf_msd, numberFrames);
    delete[] ctcf_dst;
    ctcf_dst = NULL;
    MPI_Barrier(MPI_COMM_WORLD);

    std::ofstream out;
    out.open(mypath + "_msd_pairwise_fft.dat", std::ios::out);
    for (int j = 0; j < numberFrames; j++)
        out << ctcf_msd[j] << std::endl;
    out.close();

    std::cout << rank << " is done!" << std::endl;
    delete[] ctcf_msd;
    ctcf_msd = NULL;
    MPI_Finalize();
    return 0;
}