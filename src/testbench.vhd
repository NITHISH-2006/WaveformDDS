-- testbench.vhd
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;

entity testbench is 
end testbench;

architecture rtl of testbench is

    -- ###########################################################################
    -- # SIGNALS #################################################################
    -- ###########################################################################

    -- DUT signals
    signal ui_in            : std_logic_vector(7 downto 0);
    signal uo_out           : std_logic_vector(7 downto 0);
    signal uio_in           : std_logic_vector(7 downto 0);
    signal uio_out          : std_logic_vector(7 downto 0);
    signal uio_oe           : std_logic_vector(7 downto 0);
    signal ena              : std_logic;
    signal clk              : std_logic;
    signal rst_n            : std_logic;

    -- SPI Interface
    signal spi_clk          : std_logic;
    signal spi_cs_n         : std_logic;
    signal spi_mosi         : std_logic;
    signal spi_miso         : std_logic;

    -- DDS signals
    signal fselect          : std_logic;
    signal pselect          : std_logic;
    signal dds_data         : std_logic_vector(7 downto 0);

    -- wave_select signal wired to ui_in[6:5] (Requirements: 5.1)
    signal wave_select      : std_logic_vector(1 downto 0);

    -- ###########################################################################
    -- # PROCEDURES ##############################################################
    -- ###########################################################################

    -- procedure spi_transaction
    -- This procedure communicates on a SPI interface : sends one 32b word : spi_mosi
    procedure spi_transaction (
        signal  spi_clk     : out std_logic;
        signal  spi_cs_n    : out std_logic;
        signal  spi_mosi    : out std_logic;
        constant data_tx    : in  std_logic_vector(31 downto 0)
    ) is
        variable tx_word : std_logic_vector(31 downto 0);
    begin
    
        spi_cs_n <= '0';
        spi_mosi <= data_tx(31);
        wait for 100 ns;

        tx_word := data_tx;
        tx_word := tx_word(30 downto 0) & '0';

        for index in 0 to 31 loop 

            -- Rising Edge : sample MISO signal
            spi_clk <= '1';
            wait for 50 ns;
            
            -- Falling edge : update MOSI signal
            spi_clk  <= '0';
            spi_mosi <= tx_word(31);
            tx_word := tx_word(30 downto 0) & '0';
            wait for 50 ns;

        end loop;

        wait for 100 ns;
        spi_cs_n <= '1';
        wait for 100 ns;

    end procedure spi_transaction;

begin

    -- ###############################################
    -- # Device Under Test ###########################
    -- ###############################################

    inst_tt_um_tinydds : entity work.tt_um_tinydds
    port map (
        ui_in   => ui_in,   -- input  wire [7:0] ui_in,    // Dedicated inputs
        uo_out  => uo_out,  -- output wire [7:0] uo_out,   // Dedicated outputs
        uio_in  => uio_in,  -- input  wire [7:0] uio_in,   // IOs: Input path
        uio_out => uio_out, -- output wire [7:0] uio_out,  // IOs: Output path
        uio_oe  => uio_oe,  -- output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
        ena     => ena,     -- input  wire       ena,      // will go high when the design is enabled
        clk     => clk,     -- input  wire       clk,      // clock
        rst_n   => rst_n    -- input  wire       rst_n     // reset_n - low to reset
    );

    -- ###############################################
    -- # Signals #####################################
    -- ###############################################

    ui_in(0)            <= spi_clk;
    ui_in(1)            <= spi_cs_n;
    ui_in(2)            <= spi_mosi;
    ui_in(3)            <= fselect;
    ui_in(4)            <= pselect;
    -- Task 8.1: bits 6:5 driven by wave_select; bit 7 tied low
    ui_in(6 downto 5)   <= wave_select;
    ui_in(7)            <= '0';
    uio_in              <= (others => '0');
    ena                 <= '1';
    dds_data            <= uo_out;

    -- ###############################################
    -- # Clock generation ############################
    -- ###############################################

    p_clock : process
    begin
        clk <= '0';
        wait for 10 ns;
        clk <= '1';
        wait for 10 ns;
    end process p_clock;

    -- ###############################################
    -- # Test our module #############################
    -- ###############################################

    p_test : process
        variable spi_interface_rx_word  : std_logic_vector(31 downto 0);
        -- Task 8.4: variable to track non-zero dds_output samples
        variable saw_nonzero            : boolean;
    begin

        -- Initial
        spi_clk     <= '0';
        spi_cs_n    <= '1';
        spi_mosi    <= '0';
        fselect     <= '0';
        pselect     <= '0';
        wave_select <= "00";
    
        -- Drive rst_n
        rst_n <= '0';
        wait for 200 ns;
        rst_n <= '1';
        wait for 500 ns;

        -- Check the SPI Interface : RW on SPI registers
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"0A6F_7C4F");
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"13B6_3597");
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"2A48_DF37");
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"3567_D353");
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"4216_9E7A");

        -- Task 8.2: Configure register_freq0 via SPI
        -- Address 4'h1, FTW = 28'h0053687 (>= 1 kHz at 50 MHz clock)
        -- SPI word: [31:28]=addr, [27:0]=data => x"1" & x"0053687" = x"10053687"
        -- Requirements: 5.2
        --
        -- Property 4: Phase accumulator FTW selection
        -- Feature: waveform-dds-upgrade, Property 4: phase accumulator FTW selection
        -- Validates: Requirements 2.2, 2.3
        spi_transaction(spi_clk, spi_cs_n, spi_mosi, x"10053687");

        -- Task 8.4: Assert dds_output (uo_out) is non-zero for at least one of
        -- 10 consecutive rising clock edges after reset + SPI configuration.
        -- Requirements: 5.6
        saw_nonzero := false;
        for i in 0 to 9 loop
            wait until rising_edge(clk);
            if uo_out /= x"00" then
                saw_nonzero := true;
            end if;
        end loop;
        assert saw_nonzero
            report "ASSERTION FAILED: dds_output was zero for all 10 consecutive cycles after reset + SPI config"
            severity error;

        -- Task 8.3: Drive wave_select through 00 -> 01 -> 10, holding each for >= 2 us
        -- Log transition times to transcript.
        -- Requirements: 5.1, 5.7

        -- Waveform 00: sine
        wave_select <= "00";
        wait for 2 us;

        -- Transition to 01: square
        report "wave_select transition to 01 at " & time'image(now);
        wave_select <= "01";
        wait for 2 us;

        -- Transition to 10: sawtooth
        report "wave_select transition to 10 at " & time'image(now);
        wave_select <= "10";
        wait for 2 us;

        -- End of our process
        wait;

    end process;

end rtl;
