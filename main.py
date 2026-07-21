import Danielas_app as app1
import Fayeqs_app as app2


def main():

    while True:

        print("\n========== Travel Assistant ==========")
        print("1. Flight / Hotel Assistant (Joana)")
        print("2. Tour Guide (Lou Kat Dat)")
        print("3. Start Full Travel Assistant")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":

            app1.run_chat()

        elif choice == "2":

            app2.run_chat()

        elif choice == "3":

            result = app1.run_chat()

            # Daniela requested a handoff
            if result == "handoff":

                print("\n--------------------------------")
                print("Switching to Lou Kat Dat...")
                print("--------------------------------\n")

                app2.run_chat()

        elif choice == "4":

            print("Goodbye!")
            break

        else:

            print("Please choose 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()