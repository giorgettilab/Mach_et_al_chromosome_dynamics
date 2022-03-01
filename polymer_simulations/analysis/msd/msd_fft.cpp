#include <iostream>
#include <fstream>
#include <mpi.h>
#include <string>
#include <cstring>
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

void msd_aver_single_fft(double **x, double **y, double **z, double **msd, int numframes, int numbead_b, int numbead_e, int rank)
{
    double *D, *S1, *S2;
    double Q, temp_val;
    fftw_complex *in_local_x, *in_local_y, *in_local_z;
    fftw_complex *out_local_x, *out_local_y, *out_local_z;
    fftw_complex *out2_local_x, *out2_local_y, *out2_local_z;
    D = new double[numframes + 1];
    S1 = new double[numframes];
    S2 = new double[numframes];
    in_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    in_local_y = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    in_local_z = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out_local_y = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out_local_z = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out2_local_x = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out2_local_y = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    out2_local_z = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * numframes * 2);
    for (int i = numbead_b; i < numbead_e; i++)
    {
        Q = 0.0;
        for (int j = 0; j < numframes; j++)
        {
            in_local_x[j][0] = x[i][j];
            in_local_x[j][1] = 0;
            out_local_x[j][0] = 0;
            out_local_x[j][1] = 0;
            out2_local_x[j][0] = 0;
            out2_local_x[j][1] = 0;

            in_local_y[j][0] = y[i][j];
            in_local_y[j][1] = 0;
            out_local_y[j][0] = 0;
            out_local_y[j][1] = 0;
            out2_local_y[j][0] = 0;
            out2_local_y[j][1] = 0;

            in_local_z[j][0] = z[i][j];
            in_local_z[j][1] = 0;
            out_local_z[j][0] = 0;
            out_local_z[j][1] = 0;
            out2_local_z[j][0] = 0;
            out2_local_z[j][1] = 0;
        }
        for (int j = numframes; j < 2 * numframes; j++)
        {
            in_local_x[j][0] = 0;
            in_local_x[j][1] = 0;
            out_local_x[j][0] = 0;
            out_local_x[j][1] = 0;
            out2_local_x[j][0] = 0;
            out2_local_x[j][1] = 0;

            in_local_y[j][0] = 0;
            in_local_y[j][1] = 0;
            out_local_y[j][0] = 0;
            out_local_y[j][1] = 0;
            out2_local_y[j][0] = 0;
            out2_local_y[j][1] = 0;

            in_local_z[j][0] = 0;
            in_local_z[j][1] = 0;
            out_local_z[j][0] = 0;
            out_local_z[j][1] = 0;
            out2_local_z[j][0] = 0;
            out2_local_z[j][1] = 0;
        }
        ACF(in_local_x, out_local_x, out2_local_x, 2 * numframes);
        ACF(in_local_y, out_local_y, out2_local_y, 2 * numframes);
        ACF(in_local_z, out_local_z, out2_local_z, 2 * numframes);
        for (int j = 0; j < numframes; j++)
        {
            S2[j] = out2_local_x[j][0] + out2_local_y[j][0] + out2_local_z[j][0]; // S2 is calculated
            temp_val =
                in_local_x[j][0] * in_local_x[j][0] +
                in_local_y[j][0] * in_local_y[j][0] +
                in_local_z[j][0] * in_local_z[j][0]; // D[j] is calculated
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
            msd[i][j] += S1[j] - 2 * S2[j];
        }
    }
}

void msd_aver(double **x, double **y, double **z, double *msd, double *msd_count, int numframes, int numbead_b, int numbead_e)
{
    double dx, dy, dz;
    for (int i = numbead_b; i < numbead_e; i++)
    {
        for (int j = 0; j < numframes; j++)
        {
            for (int k = j + 1; k < numframes; k++)
            {
                dx = x[i][k] - x[i][j];
                dy = y[i][k] - y[i][j];
                dz = z[i][k] - z[i][j];
                msd[k - j] += dx * dx + dy * dy + dz * dz;
                msd_count[k - j] += 1;
            }
        }
    }
}

void msd_single(double **x, double **y, double **z, double **msd, double **msd_count, int numframes, int numbead_b, int numbead_e)
{
    double dx, dy, dz;
    for (int i = numbead_b; i < numbead_e; i++)
    {
        for (int j = 0; j < numframes; j++)
        {
            for (int k = j + 1; k < numframes; k++)
            {
                dx = x[i][k] - x[i][j];
                dy = y[i][k] - y[i][j];
                dz = z[i][k] - z[i][j];
                msd[i][k - j] += dx * dx + dy * dy + dz * dz;
                msd_count[i][k - j] += 1;
            }
        }
    }
}

int main(int argc, char *argv[])
{
    int rank, commsize, ierr;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &commsize);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    int id, reg_size, unreg_size;
    int numberBeads, numberFrames;
    int flanked_number = 0;
    int start_frame = 0;
    std::string emp, line;
    std::fstream input_file;
    bool lmptrj = false;
    bool xyztrj = false;
    bool more_cols_flag = false;
    std::string mypath;
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
            std::cout << "Program to calculate MSD using lammpstrj file.\n"
                      << "Output MSD file will be in the same folder with suffix \'_msd_[a/s].dat\'."
                      << "\nIt has a single mode containing:\n"
                      << "\taverage MSD over all beads using fft and MSD per every single bead\n"
                      << "-p, --path     defines a path to a file to be analyzed\n"
                      << "-s, --start    start from this frame\n"
                      << "-f, --flanked  defines lenth of flanking segments\n"
                      << "-mc,           enables parser of additional 3 columns"
                      << "-xyz           takes xyz format for input data\n"
                      << "-lmp           takes lammpstrj format for input data " << std::endl;
            ierr = 3;
            MPI_Finalize();
            return 3;
        }

        if (strcmp(argv[i], "-p") == 0 || strcmp(argv[i], "--path") == 0)
            mypath = argv[i + 1];
        if (strcmp(argv[i], "-s") == 0 || strcmp(argv[i], "--start") == 0)
            start_frame = atoi(argv[i + 1]);
        if (strcmp(argv[i], "-f") == 0 || strcmp(argv[i], "--flanked") == 0)
            flanked_number = atoi(argv[i + 1]);
        if (strcmp(argv[i], "-lmp") == 0)
            lmptrj = true;
        if (strcmp(argv[i], "-xyz") == 0)
            xyztrj = true;
        if (strcmp(argv[i], "-mc") == 0)
            more_cols_flag = true;
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double **x, **y, **z;
    int bead_begin, bead_end, total_beads;
    int rcv_rnk;

    if (lmptrj)
    {
        input_file.open(mypath, std::ios::in);
        if (!input_file.is_open())
        {
            std::cerr << "Somthing went wrong with opening lmp file" << std::endl;
            MPI_Finalize();
            return 15;
        }
        numberFrames = 0;
        while (getline(input_file, line))
        {
            if (line.find("ITEM: NUMBER OF ATOMS") != std::string::npos)
                ++numberFrames;
        }
        if (start_frame >= numberFrames)
        {
            std::cerr << "Start frame is bigger than number of frames in file" << std::endl;
            MPI_Finalize();
            return 16;
        }
        else
        {
            numberFrames -= start_frame;
        }
        input_file.close();
        if (rank == 0)
            std::cout << "1st reading is over by " << rank << std::endl;
        input_file.open(mypath, std::ios::in);
        getline(input_file, emp);
        while (!(emp.find("ITEM: NUMBER OF ATOMS") != std::string::npos))
        {
            getline(input_file, emp);
        }
        input_file >> numberBeads;

        // consider case of flanked beads
        if (flanked_number > 0)
        {
            total_beads = numberBeads;
            if (2 * flanked_number >= numberBeads)
            {
                std::cerr << "Flanked number is bigger than number of beads" << std::endl;
                MPI_Finalize();
                return 17;
            }
            else
            {
                numberBeads -= 2 * flanked_number;
            }
        }
        else
        {
            total_beads = numberBeads;
        }
        MPI_Barrier(MPI_COMM_WORLD);
        if (rank == 0)
            std::cout << "number of frames " << numberFrames << '\n'
                      << "start frame " << start_frame << '\n'
                      << "flanked beads " << flanked_number << '\n'
                      << "number of beads " << numberBeads << std::endl;
        if (numberBeads % commsize == 0)
        {
            reg_size = int(numberBeads / commsize);
            unreg_size = reg_size;
        }
        else
        {
            reg_size = int(numberBeads / commsize);
            unreg_size = numberBeads - (commsize - 1) * reg_size;
        }
        if (rank == 0)
        {
            bead_begin = 0;
            bead_end = unreg_size;
        }
        else
        {
            bead_begin = unreg_size + (rank - 1) * reg_size;
            bead_end = unreg_size + rank * reg_size;
        }
        // adjust for flanked beads
        if (flanked_number > 0)
        {
            bead_begin += flanked_number;
            bead_end += flanked_number;
        }
        std::cout << rank << '\t' << bead_begin << '\t' << bead_end << std::endl;

        x = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            x[i] = new double[numberFrames];
        }
        y = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            y[i] = new double[numberFrames];
        }
        z = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            z[i] = new double[numberFrames];
        }

        int frame = -1;
        while (getline(input_file, emp))
        {
            frame++;
            while (!(emp.find("ITEM: ATOMS id type xu yu zu") != std::string::npos))
            {
                if (!getline(input_file, emp))
                    break;
            }
            if (frame < start_frame)
            {
                for (int i = 0; i < total_beads; i++)
                {
                    getline(input_file, emp);
                }
                continue;
            }
            else
            {
                for (int i = 0; i < total_beads; i++)
                {
                    if (input_file.peek() == EOF)
                        break;
                    input_file >> id;
                    id--;
                    if (id >= bead_begin && id < bead_end)
                    {
                        if (more_cols_flag)
                        {
                            input_file >> emp >> x[id - flanked_number][frame - start_frame] >> y[id - flanked_number][frame - start_frame] >> z[id - flanked_number][frame - start_frame] >> emp >> emp >> emp;
                        }
                        else
                            input_file >> emp >> x[id - flanked_number][frame - start_frame] >> y[id - flanked_number][frame - start_frame] >> z[id - flanked_number][frame - start_frame];
                    }
                    else
                    {
                        //input_file >> emp >> emp >> emp >> emp;
                        getline(input_file, emp);
                    }
                }
            }
        }
        input_file.close();
        if (rank == 0)
            std::cout << "2nd reading is over by " << rank << std::endl;
    }
    else if (xyztrj)
    {
        input_file.open(mypath, std::ios::in);
        if (!input_file.is_open())
        {
            std::cerr << "Somthing went wrong with opening lmp file" << std::endl;
            MPI_Finalize();
            return 15;
        }
        numberFrames = 0;
        while (getline(input_file, line))
        {
            ++numberFrames;
        }
        numberFrames = numberFrames / 1001;
        input_file.close();
        if (rank == 0)
            std::cout << "1st reading is over by " << rank << std::endl;
        input_file.open(mypath, std::ios::in);
        numberBeads = 1000;
        if (rank == 0)
            std::cout << "number of frames " << numberFrames << '\n'
                      << "number of beads " << numberBeads << std::endl;
        if (numberBeads % commsize == 0)
        {
            reg_size = int(numberBeads / commsize);
            unreg_size = reg_size;
        }
        else
        {
            reg_size = int(numberBeads / commsize);
            unreg_size = numberBeads - (commsize - 1) * reg_size;
        }
        if (rank == 0)
        {
            bead_begin = 0;
            bead_end = unreg_size;
        }
        else
        {
            bead_begin = unreg_size + (rank - 1) * reg_size;
            bead_end = unreg_size + rank * reg_size;
        }

        x = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            x[i] = new double[numberFrames];
        }
        y = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            y[i] = new double[numberFrames];
        }
        z = new double *[numberBeads];
        for (int i = 0; i < numberBeads; i++)
        {
            z[i] = new double[numberFrames];
        }

        int frame = -1;
        while (getline(input_file, emp))
        {
            frame++;
            for (int i = 0; i < numberBeads; i++)
            {
                if (input_file.peek() == EOF)
                    break;
                if (i >= bead_begin && i < bead_end)
                {
                    input_file >> x[i][frame] >> y[i][frame] >> z[i][frame];
                }
                else
                {
                    input_file >> emp >> emp >> emp;
                }
            }
        }
        input_file.close();
        if (rank == 0)
            std::cout << "2nd reading is over by " << rank << std::endl;
    }

    if (rank == 0)
        std::cout << numberBeads << ' ' << reg_size << ' ' << unreg_size << ' ' << commsize << std::endl;

    double **msd = new double *[numberBeads];
    for (int i = 0; i < numberBeads; i++)
    {
        msd[i] = new double[numberFrames];
        for (int j = 0; j < numberFrames; j++)
        {
            msd[i][j] = 0;
        }
    }

    msd_aver_single_fft(x, y, z, msd, numberFrames, bead_begin - flanked_number, bead_end - flanked_number, rank);
    for (int i = 0; i < numberBeads; i++)
    {
        delete[] x[i];
        delete[] y[i];
        delete[] z[i];
    }
    delete[] x;
    delete[] y;
    delete[] z;
    for (unsigned int i = 0; i < numberBeads; i++)
    {
        MPI_Barrier(MPI_COMM_WORLD);
        if (rank == 0 && (i >= bead_begin && i < bead_end))
            continue;
        if (rank == 0 || (i >= bead_begin && i < bead_end))
        {
            if (rank != 0)
                MPI_Send(msd[i], numberFrames, MPI_DOUBLE, 0, 1, MPI_COMM_WORLD);
            else
            {
                rcv_rnk = (i - unreg_size) / reg_size + 1;
                MPI_Recv(msd[i], numberFrames, MPI_DOUBLE, rcv_rnk, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
        }
    }
    if (rank == 0)
    {
        std::fstream fout;
        //std::cout << "PATH: " << mypath + "_msd_s_fft.dat" << std::endl;
        fout.open(mypath + "_msd_s_fft.dat", std::ios::out);
        for (unsigned int j = 0; j < numberFrames; j++)
        {
            fout << j << '\t';
            for (unsigned int i = 0; i < numberBeads; i++)
                fout << msd[i][j] << '\t';
            fout << '\n';
        }
        fout.close();
    }
    if (rank != 0)
    {
        for (unsigned int i = 0; i < numberBeads; i++)
        {
            delete[] msd[i];
        }
        delete[] msd;
    }
    else if (rank == 0)
    {
        double *msd_total = new double[numberFrames];
        for (unsigned int i = 0; i < numberFrames; i++)
        {
            for (unsigned int j = 0; j < numberBeads; j++)
            {
                msd_total[i] += msd[j][i];
            }
            msd_total[i] /= numberBeads;
        }

        std::fstream fout;
        fout.open(mypath + "_msd_a_fft.dat", std::ios::out);
        for (int i = 1; i < numberFrames; i++)
        {
            fout << i << '\t' << msd_total[i] << std::endl;
        }
        fout.close();
        delete[] msd_total;
    }
    std::cout << rank << " is done!" << std::endl;
    MPI_Finalize();
    return 0;
}
