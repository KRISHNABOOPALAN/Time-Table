from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import TimeTable, Break, TimeSlot
from .forms import TimeTableForm, AssignForm, RegisterForm
from django.template.loader import render_to_string



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "There was an error in your registration form.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})





def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")

        return redirect('login')

    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@login_required
def home(request):
    form = TimeTableForm(request.POST or None)
    timetables = TimeTable.objects.filter(user=request.user)


    if request.method == 'POST' and form.is_valid():
        tt = form.save(commit=False)
        tt.user = request.user
        tt.save()


        # Save breaks
        for i in range(int(request.POST['no_of_breaks'])):
            Break.objects.create(
                timetable=tt,
                break_number=i + 1,
                after_period=int(request.POST[f'after_period_{i+1}']),
                duration=int(request.POST[f'duration_{i+1}'])
            )

        # Generate slots for each day
        for i in range(tt.no_of_days):
            day = WEEKDAYS[i]
            start = datetime.combine(datetime.today(), tt.start_time)
            period_count = 0
            slot_no = 1
            breaks = list(tt.break_set.all())

            while period_count < tt.no_of_period:
                # Check if a break should occur after this period 
                matching_breaks = [br for br in breaks if br.after_period == period_count]
                for br in matching_breaks:
                    end = start + timedelta(minutes=br.duration)
                    TimeSlot.objects.create(
                        timetable=tt,
                        weekday=day,
                        slot_number=slot_no,
                        start_time=start.time(),
                        end_time=end.time(),
                        is_break=True
                    )
                    start = end
                    slot_no += 1
                    breaks.remove(br)  

                # Create normal period slot
                end = start + timedelta(minutes=tt.duration)
                TimeSlot.objects.create(
                    timetable=tt,
                    weekday=day,
                    slot_number=slot_no,
                    start_time=start.time(),
                    end_time=end.time(),
                    is_break=False
                )
                start = end
                period_count += 1
                slot_no += 1

        return redirect('view_timetable', pk=tt.pk)

    return render(request, 'home.html', {'form': form, 'timetables': timetables})


def get_timetable_context(tt):
    header_slots = TimeSlot.objects.filter(timetable=tt, weekday=WEEKDAYS[0]).order_by('slot_number')
    header_labels = []
    pcount = bcount = 1
    for slot in header_slots:
        if slot.is_break:
            header_labels.append((f"Break{bcount}", slot.start_time, slot.end_time))
            bcount += 1
        else:
            header_labels.append((f"Period{pcount}", slot.start_time, slot.end_time))
            pcount += 1

    data = {}
    for day in WEEKDAYS[:tt.no_of_days]:
        data[day] = TimeSlot.objects.filter(timetable=tt, weekday=day).order_by('slot_number')

    return {
        'timetable': tt,
        'days': WEEKDAYS[:tt.no_of_days],
        'header_labels': header_labels,
        'data': data,
    }


@login_required
def view_timetable(request, pk):
    tt = get_object_or_404(TimeTable, pk=pk)
    context = get_timetable_context(tt)
    return render(request, 'time_table.html', context)

@login_required
def manage_page(request, class_id):
    tt = get_object_or_404(TimeTable, id=class_id, user=request.user)
    context = get_timetable_context(tt)
    return render(request, 'manage_timetable.html', context)



def assign_subject(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    if request.method == 'POST':
        form = AssignForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('assign_modal.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = AssignForm(instance=slot)
        html = render_to_string('assign_modal.html', {'form': form}, request=request)
        return JsonResponse({'html': html})